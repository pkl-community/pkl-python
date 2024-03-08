import logging
import os
from pkl_python.evaluator.evaluator_exec import new_evaluator_with_command
from pkl_python.evaluator.evaluator_manager import EvaluatorManagerImpl
from pkl_python.evaluator.evaluator_options import EvaluatorOptions, OutputFormat
import asyncio

from pkl_python.evaluator.module_source import FileSource

async def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)
    pkl_command = os.environ.get("PKL_EXEC")
    if not pkl_command:
        raise Exception("PKL_EXEC env var must be set to path to pkl binary!")
    options = EvaluatorOptions(output_format=OutputFormat.JSON)
    manager = EvaluatorManagerImpl()
    evaluator = await manager.new_evaluator(options)
    module_path = "tests/test.pkl"
    result = await evaluator.evaluate_module(source=FileSource(module_path))
    print(result)

asyncio.run(main(), debug=True)
