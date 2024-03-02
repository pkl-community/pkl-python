import os
import pathlib
from .evaluator_options import EvaluatorOptions

PreconfiguredOptions = EvaluatorOptions(
    allowed_resources=[
        "http:",
        "https:",
        "file:",
        "env:",
        "prop:",
        "modulepath:",
        "package:",
        "projectpackage:",
    ],
    allowed_modules=[
        "pkl:",
        "repl:",
        "file:",
        "http:",
        "https:",
        "modulepath:",
        "package:",
        "projectpackage:",
    ],
    env={k: v for k, v in os.environ.items() if v is not None},
    cache_dir=str(pathlib.Path.home() / ".pkl/cache"),
)
