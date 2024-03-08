from dataclasses import dataclass
from .codes import OutgoingCode
from .base_model import BaseModel
from typing import Dict, List, Union, Optional

class ResourceReader(BaseModel):
    scheme: str
    hasHierarchicalUris: bool
    isGlobbable: bool


class ModuleReader(BaseModel):
    scheme: str
    hasHierarchicalUris: bool
    isGlobbable: bool
    isLocal: bool


class Checksums(BaseModel):
    checksums: str


class ProjectOrDependency(BaseModel):
    packageUri: Optional[str] = None
    type: Optional[str] = None
    projectFileUri: Optional[str] = None
    checksums: Optional[Checksums] = None
    dependencies: Optional[Dict[str, "ProjectOrDependency"]] = None

class CreateEvaluator(BaseModel):
    requestId: int
    clientResourceReaders: Optional[List[ResourceReader]] = None
    clientModuleReaders: Optional[List[ModuleReader]] = None
    modulePaths: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, str]] = None
    outputFormat: Optional[str] = None
    allowedModules: Optional[List[str]] = None
    allowedResources: Optional[List[str]] = None
    rootDir: Optional[str] = None
    cacheDir: Optional[str] = None
    project: Optional[ProjectOrDependency] = None
    code: OutgoingCode


class Evaluate(BaseModel):
    requestId: int
    evaluatorId: int
    moduleUri: str
    expr: Optional[str] = None
    moduleText: Optional[str] = None
    code: OutgoingCode


class ReadResource(BaseModel):
    requestId: int
    evaluatorId: int
    uri: str
    code: OutgoingCode


class ReadModule(BaseModel):
    requestId: int
    evaluatorId: int
    uri: str
    code: OutgoingCode


class ListResources(BaseModel):
    requestId: int
    evaluatorId: int
    uri: str
    code: OutgoingCode


class ListModules(BaseModel):
    requestId: int
    evaluatorId: int
    uri: str
    code: OutgoingCode


class CloseEvaluator(BaseModel):
    requestId: int
    evaluatorId: int
    code: OutgoingCode


OutgoingMessage = Union[
    CreateEvaluator,
    Evaluate,
    ReadResource,
    ReadModule,
    ListResources,
    ListModules,
    CloseEvaluator,
]
