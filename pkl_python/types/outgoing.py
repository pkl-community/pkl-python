from .codes import OutgoingCode
from pydantic import BaseModel as PydanticBaseModel
from typing import Dict, List, Union, Optional


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class ResourceReader(BaseModel):
    scheme: str
    has_hierarchical_uris: bool
    is_globbable: bool


class ModuleReader(BaseModel):
    scheme: str
    has_hierarchical_uris: bool
    is_globbable: bool
    is_local: bool


class Checksums(BaseModel):
    checksums: str


class ProjectOrDependency(BaseModel):
    package_uri: Optional[str] = None
    type: Optional[str] = None
    project_file_uri: Optional[str] = None
    checksums: Optional[Checksums] = None
    dependencies: Optional[Dict[str, "ProjectOrDependency"]] = None


class CreateEvaluator(BaseModel):
    request_id: int
    client_resource_readers: Optional[List[ResourceReader]] = None
    client_module_readers: Optional[List[ModuleReader]] = None
    module_paths: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, str]] = None
    output_format: Optional[str] = None
    allowed_modules: Optional[List[str]] = None
    allowed_resources: Optional[List[str]] = None
    root_dir: Optional[str] = None
    cache_dir: Optional[str] = None
    project: Optional[ProjectOrDependency] = None
    code: OutgoingCode


class Evaluate(BaseModel):
    request_id: int
    evaluator_id: int
    module_uri: str
    expr: Optional[str] = None
    module_text: Optional[str] = None
    code: OutgoingCode


class ReadResource(BaseModel):
    request_id: int
    evaluator_id: int
    uri: str
    code: OutgoingCode


class ReadModule(BaseModel):
    request_id: int
    evaluator_id: int
    uri: str
    code: OutgoingCode


class ListResources(BaseModel):
    request_id: int
    evaluator_id: int
    uri: str
    code: OutgoingCode


class ListModules(BaseModel):
    request_id: int
    evaluator_id: int
    uri: str
    code: OutgoingCode


class CloseEvaluator(BaseModel):
    request_id: int
    evaluator_id: int
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
