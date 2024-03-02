import os
from pkl_python.evaluator.evaluator_exec import new_evaluator_with_command
from pkl_python.evaluator.evaluator_options import EvaluatorOptions, OutputFormat
import asyncio

from pkl_python.evaluator.module_source import FileSource


async def test_evaluator():
    pkl_command = os.environ.get("PKL_EXEC")
    if not pkl_command:
        raise Exception("PKL_EXEC env var must be set to path to pkl binary!")
    options = EvaluatorOptions(output_format=OutputFormat.JSON)
    evaluator = await new_evaluator_with_command([pkl_command], options)
    module_path = "tests/test.pkl"
    result = evaluator.evaluate_module(source=FileSource(module_path))
    print(result)

asyncio.run(test_evaluator())
