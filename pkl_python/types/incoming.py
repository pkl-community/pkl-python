from typing import Dict, Optional, Tuple, Union
from pydantic import BaseModel, FileUrl
from . import codes


class IncomingMessage(BaseModel):
    pass


class CreateEvaluatorResponse(IncomingMessage):
    evaluatorId: int
    requestId: int
    error: Optional[int] = None


class EvaluateResponse(IncomingMessage):
    evaluatorId: int
    requestId: int
    result: str
    error: int


class ReadResource(IncomingMessage):
    evaluatorId: int
    requestId: int
    uri: FileUrl


class ReadModule(IncomingMessage):
    evaluatorId: int
    requestId: int
    uri: FileUrl


class Log(IncomingMessage):
    evaluatorId: int
    level: int
    message: str
    frameUri: str


class ListResources(IncomingMessage):
    evaluatorId: int
    requestId: int
    uri: FileUrl


class ListModules(IncomingMessage):
    evaluatorId: int
    requestId: int
    uri: FileUrl


IncomingMessage = Union[
    CreateEvaluatorResponse,
    EvaluateResponse,
    ReadResource,
    ReadModule,
    Log,
    ListResources,
    ListModules,
]


def decode(incoming: Tuple[int, Dict]) -> "IncomingMessage":
    code, map = incoming
    value = None
    if code == codes.EvaluateResponse:
        value = EvaluateResponse(**map, code=codes.EvaluateResponse)
    elif code == codes.EvaluateLog:
        value = Log(**map, code=codes.EvaluateLog)
    elif code == codes.NewEvaluatorResponse:
        value = CreateEvaluatorResponse(**map, code=codes.NewEvaluatorResponse)
    elif code == codes.EvaluateRead:
        value = ReadResource(**map, code=codes.EvaluateRead)
    elif code == codes.EvaluateReadModule:
        value = ReadModule(**map, code=codes.EvaluateReadModule)
    elif code == codes.ListResourcesRequest:
        value = ListResources(**map, code=codes.ListResourcesRequest)
    elif code == codes.ListModulesRequest:
        value = ListModules(**map, code=codes.ListModulesRequest)
    else:
        raise ValueError(f"Unknown code: {code}")
    return value
