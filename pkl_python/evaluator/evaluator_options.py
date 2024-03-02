from dataclasses import dataclass
from typing import Optional, Dict, List, Union
from enum import Enum
import re
from .reader import ResourceReader, ModuleReader
from ..types.project import (
    Project,
    ProjectDependencies,
    ProjectLocalDependency,
    ProjectRemoteDependency,
)


class OutputFormat(Enum):
    JSON = "json"
    JSONNET = "jsonnet"
    PCF = "pcf"
    PLIST = "plist"
    PROPERTIES = "properties"
    TEXTPROTO = "textproto"
    XML = "xml"
    YAML = "yaml"


@dataclass
class EvaluatorOptions:
    """
    EvaluatorOptions is the set of options available to control Pkl evaluation.
    """

    # properties is the set of properties available to the `prop:` resource reader.
    properties: Optional[Dict[str, str]] = None

    # env is the set of environment variables available to the `env:` resource reader.
    env: Optional[Dict[str, str]] = None

    # modulePaths is the set of directories, ZIP archives, or JAR archives to search when
    # resolving `modulepath`: resources and modules.
    #
    # This option must be non-emptyMirror if ModuleReaderModulePath or ResourceModulePath are used.
    module_paths: Optional[List[str]] = None

    # outputFormat controls the renderer to be used when rendering the `output.text`
    # property of a module.
    output_format: Optional[OutputFormat] = None

    # allowedModules is the URI patterns that determine which modules can be loaded and evaluated.
    allowed_modules: Optional[List[str]] = None

    # allowedResources is the URI patterns that determine which resources can be loaded and evaluated.
    allowed_resources: Optional[List[str]] = None

    # resourceReaders are the resource readers to be used by the evaluator.
    resource_readers: Optional[List["ResourceReader"]] = None

    # moduleReaders are the set of custom module readers to be used by the evaluator.
    module_readers: Optional[List["ModuleReader"]] = None

    # cacheDir is the directory where `package:` modules are cached.
    #
    # If empty, no cacheing is performed.
    cache_dir: Optional[str] = None

    # rootDir is the root directory for file-based reads within a Pkl program.
    #
    # Attempting to read past the root directory is an error.
    root_dir: Optional[str] = None

    # ProjectDir is the project directory for the evaluator.
    #
    # Setting this determines how Pkl resolves dependency notation imports.
    # It causes Pkl to look for the resolved dependencies relative to this directory,
    # and load resolved dependencies from a PklProject.deps.json file inside this directory.
    #
    # NOTE:
    # Setting this option is not equivalent to setting the `--project-dir` flag from the CLI.
    # When the `--project-dir` flag is set, the CLI will evaluate the PklProject file,
    # and then applies any evaluator settings and dependencies set in the PklProject file
    # for the main evaluation.
    #
    # In contrast, this option only determines how Pkl considers whether files are part of a
    # project.
    # It is meant to be set by lower level logic in TS that first evaluates the PklProject,
    # which then configures EvaluatorOptions accordingly.
    #
    # To emulate the CLI's `--project-dir` flag, create an evaluator with NewProjectEvaluator,
    # or EvaluatorManager.NewProjectEvaluator.
    project_dir: Optional[str] = None

    # declaredProjectDependencies is set of dependencies available to modules within ProjectDir.
    #
    # When importing dependencies, a PklProject.deps.json file must exist within ProjectDir
    # that contains the project's resolved dependencies.
    declared_project_dependencies: Optional[ProjectDependencies] = None


def encoded_dependencies(
    input: ProjectDependencies,
) -> Dict[str, Union[ProjectLocalDependency, ProjectRemoteDependency]]:
    deps = {**input.local_dependencies, **input.remote_dependencies}
    deps_message = {
        key: {
            "packageUri": dep.package_uri,
            "projectFileUri": dep.project_file_uri
            if isinstance(dep, ProjectLocalDependency)
            else None,
            "type": "local" if isinstance(dep, ProjectLocalDependency) else "remote",
            "checksums": None
            if isinstance(dep, ProjectLocalDependency)
            else {"checksums": dep.checksums.sha256},
            "dependencies": encoded_dependencies(dep.dependencies)
            if isinstance(dep, ProjectLocalDependency)
            else None,
        }
        for key, dep in deps.items()
    }

    return deps_message


def with_project(project: Project) -> EvaluatorOptions:
    return EvaluatorOptions(
        **with_project_evaluator_settings(project), **with_project_dependencies(project)
    )


def with_project_evaluator_settings(
    project: Project,
) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
    if project.evaluator_settings:
        return {
            "properties": project.evaluator_settings.external_properties,
            "env": project.evaluator_settings.env,
            "allowed_modules": project.evaluator_settings.allowed_modules,
            "allowed_resources": project.evaluator_settings.allowed_resources,
            "cache_dir": None
            if project.evaluator_settings.no_cache
            else project.evaluator_settings.module_cache_dir,
            "root_dir": project.evaluator_settings.root_dir,
        }
    else:
        return {}


def with_project_dependencies(project: Project) -> EvaluatorOptions:
    return EvaluatorOptions(
        project_dir=re.sub(r"^file://|/PklProject$", "", project.project_file_uri),
        declared_project_dependencies=project.dependencies,
    )
