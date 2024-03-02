from . import evaluator_exec as exec
from .module_source import FileSource
from .preconfigured_options import PreconfiguredOptions
from ..types.evaluator import Evaluator
from pkl_python.types.project import Project


async def load_project(path: str) -> Project:
    ev = await exec.new_evaluator(PreconfiguredOptions)
    return await load_project_from_evaluator(ev, path)


async def load_project_from_evaluator(ev: "Evaluator", path: str) -> Project:
    return await ev.evaluate_output_value(FileSource(path))
