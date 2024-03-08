import unittest
import json
from pkl_python.evaluator.evaluator_manager import create_evaluator_request, pack_message
import msgpack
from pkl_python.types.codes import NewEvaluator
from pkl_python.evaluator.evaluator_options import EvaluatorOptions
from pkl_python.types.outgoing import ModuleReader

class TestEvaluatorManager(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_create_evaluator_request(self):
        _, req = create_evaluator_request(EvaluatorOptions(
            allowed_modules=["pkl:", "repl:", "file:", "customfs:"],
            module_readers=[
                ModuleReader(scheme="customfs", hasHierarchicalUris=True, isGlobbable=True, isLocal=True)
            ]
        ))
        msg = pack_message(msgpack.Packer(), NewEvaluator, req.model_dump(exclude_none=True))   
        expected_code = 0x20
        expected_msg = {   "requestId": 135,
                        "allowedModules": ["pkl:", "repl:", "file:", "customfs:"],
                        "clientModuleReaders": [
                            {
                                "scheme": "customfs",
                                "hasHierarchicalUris": True,
                                "isGlobbable": True,
                                "isLocal": True
                            }
                        ]
                    }
        actual_code, actual_msg = msgpack.unpackb(msg)
        self.assertEqual(expected_code, actual_code)
        self.assertDictEqual(expected_msg, actual_msg)