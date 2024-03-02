# Evaluator is an interface for evaluating Pkl modules.
from abc import ABC, abstractmethod
from typing import Any, Dict

from ..evaluator.module_source import ModuleSource


class Evaluator(ABC):
    # evaluateModule evaluates the given module, and writes it to the value pointed by
    # out.
    #
    # This method is designed to work with TS modules that have been code generated from Pkl
    # sources.
    @abstractmethod
    def evaluate_module(self, source: ModuleSource) -> Any:
        pass

    # evaluateOutputText evaluates the `output.text` property of the given module.
    @abstractmethod
    def evaluate_output_text(self, source: ModuleSource) -> str:
        pass

    # evaluateOutputValue evaluates the `output.value` property of the given module,
    # and writes to the value pointed by out.
    @abstractmethod
    def evaluate_output_value(self, source: ModuleSource) -> Any:
        pass

    # evaluateOutputFiles evaluates the `output.files` property of the given module.
    @abstractmethod
    def evaluate_output_files(self, source: ModuleSource) -> Dict[str, str]:
        pass

    # evaluateExpression evaluates the provided expression on the given module source, and writes
    # the result into the value pointed by out.
    @abstractmethod
    def evaluate_expression(self, source: ModuleSource, expr: str) -> Any:
        pass

    # evaluateExpressionRaw evaluates the provided module, and returns the underlying value's raw
    # bytes.
    #
    # This is a low level API.
    @abstractmethod
    def evaluate_expression_raw(self, source: ModuleSource, expr: str) -> bytes:
        pass

    # close closes the evaluator and releases any underlying resources.
    @abstractmethod
    def close(self) -> None:
        pass

    # closed tells if this evaluator is closed.
    @property
    @abstractmethod
    def closed(self) -> bool:
        pass
