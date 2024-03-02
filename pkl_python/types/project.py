from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Checksums:
    sha256: str


@dataclass
class ProjectRemoteDependency:
    package_uri: str
    checksums: Checksums


@dataclass
class ProjectLocalDependency:
    package_uri: str
    project_file_uri: str
    dependencies: ProjectDependencies


@dataclass
class ProjectDependencies:
    local_dependencies: Dict[str, ProjectLocalDependency]
    remote_dependencies: Dict[str, ProjectRemoteDependency]


@dataclass
class ProjectPackage:
    name: str
    base_uri: str
    version: str
    package_zip_url: str
    description: str
    authors: List[str]
    website: str
    documentation: str
    source_code: str
    source_code_url_scheme: str
    license: str
    license_text: str
    issue_tracker: str
    api_tests: List[str]
    exclude: List[str]
    uri: List[str]


@dataclass
class ProjectEvaluatorSettings:
    external_properties: Dict[str, str]
    env: Dict[str, str]
    allowed_modules: List[str]
    allowed_resources: List[str]
    module_path: List[str]
    module_cache_dir: str
    root_dir: str
    no_cache: Optional[bool] = None


@dataclass
class Project:
    project_file_uri: str
    tests: List[str]
    dependencies: ProjectDependencies
    package: Optional[ProjectPackage] = None
    evaluator_settings: Optional[ProjectEvaluatorSettings] = None
