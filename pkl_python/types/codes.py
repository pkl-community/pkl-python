from typing import Union

# Constants
NewEvaluator = 0x20
NewEvaluatorResponse = 0x21
CloseEvaluator = 0x22
Evaluate = 0x23
EvaluateResponse = 0x24
EvaluateLog = 0x25
EvaluateRead = 0x26
EvaluateReadResponse = 0x27
EvaluateReadModule = 0x28
EvaluateReadModuleResponse = 0x29
ListResourcesRequest = 0x2A
ListResourcesResponse = 0x2B
ListModulesRequest = 0x2C
ListModulesResponse = 0x2D

# Type alias for OutgoingCode
OutgoingCode = Union[
    NewEvaluator,
    CloseEvaluator,
    Evaluate,
    EvaluateReadResponse,
    EvaluateReadModuleResponse,
    ListResourcesResponse,
    ListModulesResponse,
]
