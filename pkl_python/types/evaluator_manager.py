from abc import ABC, abstractmethod
from ..types.evaluator import Evaluator
from ..evaluator.evaluator_options import EvaluatorOptions


class EvaluatorManagerInterface(ABC):
    @abstractmethod
    def close(self) -> None:
        """
        Closes the evaluator manager and all of its evaluators.

        If running Pkl as a child process, closes all evaluators as well as the child process.
        If calling into Pkl through the C API, close all existing evaluators.
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        pass

    @abstractmethod
    def new_evaluator(self, opts: EvaluatorOptions) -> Evaluator:
        """
        Constructs an evaluator instance.

        If calling into Pkl as a child process, the first time NewEvaluator is called, this will
        start the child process.
        """
        pass

    @abstractmethod
    def new_project_evaluator(
        self, project_dir: str, opts: EvaluatorOptions
    ) -> Evaluator:
        """
        An easy way to create an evaluator that is configured by the specified projectDir.

        It is similar to running the `pkl eval` or `pkl test` CLI command with a set `--project-dir`.

        When using project dependencies, they must first be resolved using the `pkl project resolve`
        CLI command.
        """
        pass
