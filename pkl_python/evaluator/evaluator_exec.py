from pkl_python.evaluator.project import load_project_from_evaluator
from pkl_python.evaluator.evaluator_options import EvaluatorOptions, with_project
from pkl_python.evaluator.evaluator import Evaluator
from pkl_python.evaluator.evaluator_manager import new_evaluator_manager_with_command
from typing import List
from .preconfigured_options import PreconfiguredOptions


# newEvaluator returns an evaluator backed by a single EvaluatorManager.
# Its manager gets closed when the evaluator is closed.
#
# If creating multiple evaluators, prefer using EvaluatorManager.new_evaluator instead,
# because it lessens the overhead of each successive evaluator.
def new_evaluator(opts: EvaluatorOptions) -> "Evaluator":
    return new_evaluator_with_command([], opts)


# newProjectEvaluator is an easy way to create an evaluator that is configured by the specified
# projectDir.
#
# It is similar to running the `pkl eval` or `pkl test` CLI command with a set `--project-dir`.
#
# When using project dependencies, they must first be resolved using the `pkl project resolve`
# CLI command.
def new_project_evaluator(project_dir: str, opts: EvaluatorOptions) -> Evaluator:
    return new_project_evaluator_with_command(project_dir, [], opts)


# newProjectEvaluatorWithCommand is like newProjectEvaluator, but also accepts the Pkl command to run.
#
# The first element in pklCmd is treated as the command to run.
# Any additional elements are treated as arguments to be passed to the process.
# pklCmd is treated as the base command that spawns Pkl.
# For example, the below snippet spawns the command /opt/bin/pkl.
#
# newProjectEvaluatorWithCommand(context.Background(), ["/opt/bin/pkl"], "/path/to/my/project")
#
# If creating multiple evaluators, prefer using EvaluatorManager.new_project_evaluator instead,
# because it lessens the overhead of each successive evaluator.
def new_project_evaluator_with_command(
    project_dir: str, pkl_cmd: List[str], opts: EvaluatorOptions
) -> Evaluator:
    manager = new_evaluator_manager_with_command(pkl_cmd)
    project_evaluator = new_evaluator(PreconfiguredOptions)
    project = load_project_from_evaluator(
        project_evaluator, f"{project_dir}/PklProject"
    )
    return manager.new_evaluator({**with_project(project), **opts})


# newEvaluatorWithCommand is like newEvaluator, but also accepts the Pkl command to run.
#
# The first element in pklCmd is treated as the command to run.
# Any additional elements are treated as arguments to be passed to the process.
# pklCmd is treated as the base command that spawns Pkl.
# For example, the below snippet spawns the command /opt/bin/pkl.
#
# newEvaluatorWithCommand(context.Background(), ["/opt/bin/pkl"])
#
# If creating multiple evaluators, prefer using EvaluatorManager.new_evaluator instead,
# because it lessens the overhead of each successive evaluator.
def new_evaluator_with_command(pkl_cmd: List[str], opts: EvaluatorOptions) -> Evaluator:
    manager = new_evaluator_manager_with_command(pkl_cmd)
    return manager.new_evaluator(opts)
