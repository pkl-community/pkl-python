import asyncio
from .project import load_project_from_evaluator
from ..types.evaluator_manager import EvaluatorManagerInterface
from .evaluator import EvaluatorImpl, Evaluator
from ..types.outgoing import CreateEvaluator, OutgoingMessage, ProjectOrDependency
import msgpack
from ..types import codes
from .evaluator_options import encoded_dependencies, EvaluatorOptions, with_project
from .preconfigured_options import PreconfiguredOptions
from ..types.incoming import CreateEvaluatorResponse, decode
import re
import os
import subprocess
from typing import List, Tuple
import logging

log = logging.getLogger(__name__)

def new_evaluator_manager() -> EvaluatorManagerInterface:
    """
    Creates a new EvaluatorManager.
    """
    return new_evaluator_manager_with_command([])


def new_evaluator_manager_with_command(
    pkl_command: List[str],
) -> EvaluatorManagerInterface:
    """
    Creates a new EvaluatorManager using the given pkl command.

    The first element in pklCmd is treated as the command to run.
    Any additional elements are treated as arguments to be passed to the process.
    pklCmd is treated as the base command that spawns Pkl.
    For example, the below snippet spawns the command /opt/bin/pkl.

    newEvaluatorManagerWithCommand(["/opt/bin/pkl"])
    """
    return EvaluatorManagerImpl(pkl_command)


semver_pattern = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)
pkl_version_regex = re.compile(f"Pkl ({semver_pattern.pattern}).*")


class EvaluatorManagerImpl(EvaluatorManagerInterface):
    def __init__(self, pkl_command: list = []):
        self.pkl_command = pkl_command
        self.pending_evaluators = {}
        self.evaluators = {}
        self.packer = msgpack.Packer()
        self.unpacker = msgpack.Unpacker()
        self.closed = False
        self.cmd = None
        self.listener_ready = asyncio.Event()
        self.buffer_bytes = 128

    async def start(self):
        if self.closed:
            raise Exception("EvaluatorManager has been closed")
        if not self.cmd:
            program, args = self.get_start_command()
            print(program, args)
            self.cmd = await asyncio.create_subprocess_exec(
                program,
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            asyncio.create_task(self.log_stderr())
            self.listener = asyncio.create_task(self.listen())
            await self.listener_ready.wait()

    async def log_stderr(self):
        while not self.cmd.stderr.at_eof():
            stderr_line = await self.cmd.stderr.readline()
            log.info(stderr_line)

    def handle_close(self):
        for future in self.pending_evaluators.values():
            future.cancel()
        errors = []
        for ev in self.evaluators.values():
            try:
                ev.close()
            except Exception as e:
                errors.append(e)
        self.closed = True
        if errors:
            print("errors closing evaluators:", errors)

    def get_command_and_arg_strings(self) -> Tuple[str, List[str]]:
        if self.pkl_command:
            return self.pkl_command[0], self.pkl_command[1:]
        pkl_exec_env = os.environ.get("PKL_EXEC", "")
        if pkl_exec_env:
            parts = pkl_exec_env.split(" ")
            return parts[0], parts[1:]
        return "pkl", []

    def get_evaluator(self, evaluator_id: int) -> EvaluatorImpl | None:
        ev = self.evaluators.get(evaluator_id)
        if not ev:
            print("Received unknown evaluator id:", evaluator_id)
        return ev

    def handle_decode(self, item):
        decoded = decode(item)
        log.info(decoded)
        if type(decoded) is CreateEvaluatorResponse:
            id = decoded.requestId
            pending = self.pending_evaluators.get(id)
            if not pending:
                log.warning(f"received a message for an unknown request id: {decoded.requestId}")
            else:
                pending.set_result(decoded)
        else:
            ev = self.get_evaluator(decoded.evaluator_id)
            log.info(f"Received message for evaluator {decoded.evaluator_id} with code {decoded.code}")
            if not ev:
                log.error(f"No evaluator ID in message: {decoded}")
                pass
            if decoded.code == codes.EvaluateResponse:
                ev.handle_evaluate_response(decoded)
            elif decoded.code == codes.EvaluateLog:
                ev.handle_log(decoded)
            elif decoded.code == codes.EvaluateRead:
                ev.handle_read_resource(decoded)
            elif decoded.code == codes.EvaluateReadModule:
                ev.handle_read_module(decoded)
            elif decoded.code == codes.ListResourcesRequest:
                ev.handle_list_resources(decoded)
            elif decoded.code == codes.ListModulesRequest:
                ev.handle_list_modules(decoded)

    async def listen(self):
        log.info("listener started")
        self.listener_ready.set()
        while not self.cmd.stdout.at_eof():
            log.info("waiting for message")
            try:
                data = await self.cmd.stdout.read(self.buffer_bytes)
                log.info(f"stdout: {data}")
                self.unpacker.feed(data)
                item = self.unpacker.unpack()
                log.info(item)
                self.handle_decode(item)
            except asyncio.IncompleteReadError:
                break
            except msgpack.OutOfData:
                continue                

    def get_start_command(self) -> Tuple[str, List[str]]:
        cmd, args = self.get_command_and_arg_strings()
        return cmd, [*args, "server"]

    def close(self):
        self.cmd.kill()

    def get_version(self) -> str:
        if self.version:
            return self.version
        cmd, args = self.get_command_and_arg_strings()
        result = subprocess.run([cmd, *args, "--version"], stdout=subprocess.PIPE)
        version = re.search(self.pkl_version_regex, result.stdout.decode())
        if not version or len(version.groups()) < 2:
            raise Exception(
                f"failed to get version information from Pkl. Ran '{' '.join(args)}', and got stdout \"{result.stdout.decode}\""
            )
        self.version = version.group(1)
        return self.version

    async def new_evaluator(self, opts):
        if not self.cmd:
            await self.start()

        id, req = create_evaluator_request(opts)
        future = asyncio.Future()
        if id in self.pending_evaluators:
            raise Exception(f"Request ID {id} already exists")
        self.pending_evaluators[id] = future

        await send(self.cmd.stdin, pack_message(self.packer, codes.NewEvaluator, req.model_dump(exclude_none=True)))
        log.info("Sent create evaluator request")

        # while not self.cmd.stderr.at_eof():
        #     stderr_line = await self.cmd.stderr.readline()
        #     log.info(stderr_line)

        response = await future
        log.info("Received create evaluator response")
        print(response)
        ev = EvaluatorImpl(response.evaluatorId, self)
        self.evaluators[response.evaluatorId] = ev
        return ev

    async def new_project_evaluator(
        self, project_dir: str, opts: "EvaluatorOptions"
    ) -> Evaluator:
        project_evaluator = self.new_evaluator(PreconfiguredOptions)
        project = load_project_from_evaluator(
            project_evaluator, f"{project_dir}/PklProject"
        )

        return self.new_evaluator({**with_project(project), **opts.__dict__})
    
def pack_message(packer: msgpack.Packer, code: codes.OutgoingCode, msg) -> bytearray:
        return packer.pack([code, msg]) 

def create_evaluator_request(opts: EvaluatorOptions) -> CreateEvaluator:
    request_id = 135
    create_evaluator = CreateEvaluator(
        requestId=request_id,
        allowedModules=opts.allowed_modules,
        clientResourceReaders=opts.resource_readers,
        clientModuleReaders=opts.module_readers,
        code=codes.NewEvaluator,
    )

    if opts.project_dir:
        create_evaluator.project = ProjectOrDependency(
            projectFileUri=f"file://{opts.project_dir}/PklProject",
            dependencies=encoded_dependencies(opts.declared_project_dependencies)
            if opts.declared_project_dependencies
            else None,
        )
    return request_id, create_evaluator

async def send(stdin, out):
    stdin.write(out)
    await stdin.drain()

