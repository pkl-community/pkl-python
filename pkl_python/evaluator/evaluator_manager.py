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
    def __init__(self, pkl_command: list):
        self.pkl_command = pkl_command
        self.pending_evaluators = {}
        self.evaluators = []
        self.encoder = msgpack.Packer()
        self.decoder = msgpack.Unpacker()
        self.closed = False
        self.cmd = None

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
            self.listener = asyncio.create_task(self.listen())

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

    async def send(self, out: "OutgoingMessage"):
        self.cmd.stdin.write(pack_message(self.encoder, out))
        await self.cmd.stdin.drain()

    def get_evaluator(self, evaluator_id: int) -> EvaluatorImpl | None:
        ev = self.evaluators.get(evaluator_id)
        if not ev:
            print("Received unknown evaluator id:", evaluator_id)
        return ev

    async def listen(self):
        while not self.cmd.stdout.at_eof():
            line = await self.cmd.stdout.readline()
            stdout_line = await self.cmd.stdout.readline()
            print(f"stdout: {stdout_line}")
            self.decoder.feed(line)
            for item in self.decoder:
                decoded = decode(item)
                if decoded.code == codes.NewEvaluatorResponse:
                    id = str(decoded.request_id)
                    pending = self.pending_evaluators.get(id)
                    if not pending:
                        print(
                            "warn: received a message for an unknown request id:",
                            decoded.request_id,
                        )
                    else:
                        pending.set_result(decoded)
                else:
                    ev = self.get_evaluator(decoded.evaluator_id)
                    if not ev:
                        continue
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

        request_id = 0
        create_evaluator = CreateEvaluator(
            request_id=request_id,  # TODO
            client_resource_readers=opts.resource_readers or [],
            client_module_readers=opts.module_readers or [],
            code=codes.NewEvaluator,
            **opts.__dict__,
        )

        if opts.project_dir:
            create_evaluator.project = ProjectOrDependency(
                projectFileUri=f"file://{opts.project_dir}/PklProject",
                dependencies=encoded_dependencies(opts.declared_project_dependencies)
                if opts.declared_project_dependencies
                else None,
            )

        future = asyncio.Future()
        self.pending_evaluators[request_id] = future

        await self.send(create_evaluator)

        stderr_line = await self.cmd.stderr.readline()
        if stderr_line:  # read from stderr
            raise Exception(f"Failed to start Evaluator: {stderr_line}")

        response = await future
        print(response)
        response = CreateEvaluatorResponse(**response)
        ev = EvaluatorImpl(response.evaluator_id, self)
        self.evaluators[response.evaluator_id] = ev

        return ev

    async def new_project_evaluator(
        self, project_dir: str, opts: "EvaluatorOptions"
    ) -> Evaluator:
        project_evaluator = self.new_evaluator(PreconfiguredOptions)
        project = load_project_from_evaluator(
            project_evaluator, f"{project_dir}/PklProject"
        )

        return self.new_evaluator({**with_project(project), **opts.__dict__})


def pack_message(packer: msgpack.Packer, msg: OutgoingMessage) -> bytearray:
    code, *rest = msg
    return packer.pack([code, rest])
