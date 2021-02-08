#!/usr/bin/env python3

# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re
import subprocess
from collections import defaultdict
import argparse


class ArtifactManager(object):
    artifacts = []

    def __init__(self, artifacts=None):
        if artifacts:
            self.artifacts = artifacts

    def add(self, artifact):
        """Add an artifact.

        Args:
            artifact (Artifact): The artifact to add.
        """
        if self.find(artifact.name, artifact.source) is None:
            artifact.append(artifact)

    def find(self, name, source):
        """Find the index of an artifact based on its name and source.

        Args:
            name (str): The name of the artifact.
            source (str): The source type of the artifact.

        Returns:
            int: The index of the artifact, or None if not found.
        """
        for index, artifact in enumerate(self.artifacts):
            if artifact.name == name and artifact.source == source:
                return index
        return None

    def get_from_path(self, path):
        """Get an artifact based on a path.

        Args:
            path (str): The path to use for search.

        Returns:
            Artifact: the artifact corresponding to the provided path, or None if not found.
        """
        name, source = get_name_and_source_from_path(path)
        for artifact in self.artifacts:
            if artifact.name == name and artifact.source == source:
                return artifact
        return None

    def get_artifacts_with_matching_source(self, source):
        """Get all artifacts with a particular source type.

        Args:
            source (str): The source type of the artifacts to retrieve.

        Returns:
            list[Artifact]: A list of all artifacts with a matching source type.
        """
        artifacts_with_matching_source = []
        for artifact in self.artifacts:
            if artifact.source == source:
                artifacts_with_matching_source.append(artifact)
        return artifacts_with_matching_source

    def get_dependencies_from_paths(self, paths):
        """Get a combined list of dependencies for Artifacts matching provided paths.

        Args:
            paths (list[str]): A list of paths to retrieve dependencies from.

        Returns:
            list[Dependency]: A list of dependencies for Artifacts matching provided paths.
        """
        dependencies, already_added = self._get_dependencies(paths)
        return dependencies

    def _get_dependencies(self, paths, index=0):
        """Recursive helper method for get_dependencies_from_paths.

        Args:
            paths (list[str]): A list of paths to retrieve dependencies from.
            index (int, optional): The index of the current path in the list of paths. Defaults to 0.

        Returns:
            tuple(list[Dependency], defaultdict): The current list of identified dependencies.
        """
        if len(paths) == 0:
            return []
        if index == len(paths) - 1:
            dependencies = []
            already_added = defaultdict(list)
        else:
            dependencies, already_added = self._get_dependencies(paths, index + 1)
        artifact = self.get_from_path(paths[index])
        if artifact:
            for item in artifact.dependencies:
                if item.source not in already_added[item.name]:
                    dependencies.append(item)
                    already_added[item.name].append(item.source)
        return dependencies, already_added

    def get_artifacts_with_dependency(self, artifacts_depended_on, source=None):
        """Get a list of artifacts that are dependent on one or more of the specified artifacts.

        Args:
            artifacts_depended_on (list[Artifact]): A list of artifacts that are depended on.
            source (str, optional): Limit artifacts to search for dependency to those with corresponding source. Defaults to None.

        Returns:
            list[Artifact]: A list of artifacts that have a dependency on one or more of the specified artifacts.
        """
        artifacts_with_potential_dependency = self.artifacts
        if source:
            artifacts_with_potential_dependency = (
                self.get_artifacts_with_matching_source(source)
            )
        dependent_artifacts, already_added = self._get_artifacts_with_dependency_helper(
            artifacts_depended_on, artifacts_with_potential_dependency
        )
        return dependent_artifacts

    def _get_artifacts_with_dependency_helper(
        self, artifacts_depended_on, artifacts_with_potential_dependency, index=0
    ):
        """Recursive helper method for get_artifacts_with_dependency.

        Args:
            artifacts_depended_on (list[Artifact]): A list of artifacts that are depended on.
            artifacts_with_potential_dependency (list[Artifact]): A list of artifacts to search for dependencies.
            index (int, optional): The index of the current artifact in the list of artifacts. Defaults to 0.

        Returns:
            tuple(list[Artifact], defaultdict): A list of artifacts that have a dependency on one or more of the specified artifacts.
        """
        if len(artifacts_depended_on) == 0:
            return [], None
        if index == len(artifacts_depended_on) - 1:
            dependent_artifacts = []
            already_added = defaultdict(list)
        else:
            (
                dependent_artifacts,
                already_added,
            ) = self._get_artifacts_with_dependency_helper(
                artifacts_depended_on, artifacts_with_potential_dependency, index + 1
            )
        for artifact in artifacts_with_potential_dependency:
            if artifact.source not in already_added[artifact.name]:
                if artifact.has_dependency(
                    artifacts_depended_on[index],
                ):
                    dependent_artifacts.append(artifact)
                    already_added[artifact.name].append(artifact.source)
        return dependent_artifacts, already_added


class Artifact(object):
    """Represents a file in Ansible collection hierarchy."""

    name = None
    source = None
    path = None
    dependencies = []

    def __init__(self, name, source, path, dependencies=None):
        """Instantiate an Artifact

        Args:
            name (str): The name of the artifact.
            source (str): The source type of the artifact.
            path (str): The absolute path of the artifact.
            dependencies (list[Dependency], optional): A list of dependencies this artifact has on other artifacts. Defaults to None.
        """
        self.name = name
        self.source = source
        self.path = path
        if dependencies:
            self.dependencies = dependencies

    @classmethod
    def from_path(cls, path):
        """Instantiate an Artifact based on provided path.

        Args:
            path (str): The path to an artifact in an Ansible collection.

        Returns:
            Artifact: an artifact object.
        """
        name, source = get_name_and_source_from_path(path)
        dependencies = []
        if source == "module" or source == "module_util" or source == "test":
            module_utils = get_module_util_dependencies_in_file(path)
            for util in module_utils:
                dependencies.append(Dependency(util, "module_util"))
        if source == "test" or source == "helper":
            modules = get_module_dependencies_in_test_file(path)
            for module in modules:
                dependencies.append(Dependency(module, "module"))
        if source == "test":
            helpers = get_helper_dependencies_in_test_file(path)
            for helper in helpers:
                dependencies.append(Dependency(helper, "helper"))

        return cls(name, source, path, dependencies)

    def __eq__(self, other):
        if not isinstance(other, (Artifact, Dependency)):
            return NotImplemented
        return self.name == other.name and self.source == other.source

    def __hash__(self):
        return hash(self.name + self.source)

    def has_dependency(self, potential_dependency):
        """Determines if artifact has a dependency on another artifact.

        Args:
            potential_dependency (union[Artifact, Dependency]): The potential dependency to search for in artifact's dependencies.

        Returns:
            bool: If the artifact is dependent or not.
        """
        for dependency in self.dependencies:
            if dependency == potential_dependency:
                return True
        return False


class Dependency(object):
    """Represents an Artifact dependency."""

    name = None
    source = None

    def __init__(self, name, source):
        """Instantiate a Dependency.

        Args:
            name (str): The name of the artifact.
            source (str): The source type of the artifact.
        """
        self.name = name
        self.source = source

    def __eq__(self, other):
        if not isinstance(other, (Artifact, Dependency)):
            return NotImplemented
        return self.name == other.name and self.source == other.source

    def __hash__(self):
        return hash(self.name + self.source)


def get_name_and_source_from_path(path):
    """Determine the artifact name and source type based on its path.

    Args:
        path (str): The path to an artifact in an Ansible collection.

    Returns:
        tuple(str, str): The name and source of an artifact based on its path.
    """
    name = os.path.splitext(path.split("/")[-1])[0]
    if "plugins/modules/" in path or "plugins/action/" in path:
        source = "module"
    elif "plugins/module_utils/" in path:
        source = "module_util"
    elif "tests/functional" in path or "tests/unit" in path:
        source = "test"
    elif "tests/helpers" in path:
        source = "helper"
    else:
        source = "invalid"
    return name, source


def get_module_util_dependencies_in_file(path):
    """Scrape file for module_utils imports.

    Args:
        path (str): The path to scrape.

    Returns:
        list[str]: A list of module_utils imports found in the file.
    """
    content = ""
    with open(path, "r") as f:
        content = f.read()
    module_utils = []
    module_utils += re.findall(
        r"from\s+ansible_collections\.ibm\."
        + collection_to_use
        + r"\.plugins\.module_utils\s+import\s*\(([^\)]+)\)",
        content,
        re.MULTILINE,
    )
    module_utils += re.findall(
        r"from\s+ansible_collections\.ibm\."
        + collection_to_use
        + r"\.plugins\.module_utils\s+import\s+([^\n\(\)]+)",
        content,
        re.MULTILINE,
    )
    module_utils += re.findall(
        r"from\s+ansible_collections\.ibm\."
        + collection_to_use
        + r"\.plugins\.module_utils\.([^\s]+)\s+import",
        content,
        re.MULTILINE,
    )
    module_utils += re.findall(
        r"import\s+ansible_collections\.ibm\."
        + collection_to_use
        + r"\.plugins\.module_utils\.([^\s]+)",
        content,
        re.MULTILINE,
    )
    module_utils = ", ".join(module_utils).replace("\n", ",")
    module_utils = re.sub(r"as\s+[a-zA-Z0-9\_]+", "", module_utils)
    module_utils = module_utils.replace(",", " ")
    module_utils = re.split(r"\s+", module_utils.strip())
    module_utils = list(set(module_utils))
    return module_utils


def get_module_dependencies_in_test_file(path):
    """Scrape test file for module dependencies.

    Args:
        path (str): The path to scrape.

    Returns:
        list[str]: A list of module dependencies found in the file.
    """
    content = ""
    with open(path, "r") as f:
        content = f.read()
    modules = []
    modules += re.findall(r"\.all\.([a-zA-Z0-9\_]+)\(", content)
    modules += re.findall(
        r"[\"\']" + collection_to_use + r"\.plugins\.modules\.([^\"\']+)[\"\']",
        content,
    )
    modules = list(set(modules))
    return modules


def get_helper_dependencies_in_test_file(path):
    """Scrape test file for helper dependencies.

    Args:
        path (str): The path to scrape.

    Returns:
        list[str]: A list of helper dependencies found in the file.
    """
    content = ""
    with open(path, "r") as f:
        content = f.read()
    helpers = []
    helpers += re.findall(
        r"from\s+" + collection_to_use + r"\.tests\.helpers\.([^\s]+)\s+import",
        content,
        re.MULTILINE,
    )
    helpers += re.findall(
        r"from\s+" + collection_to_use + r"\.tests\.helpers\s+import\s*\(([^\)]+)\)",
        content,
        re.MULTILINE,
    )
    helpers += re.findall(
        r"from\s+" + collection_to_use + r"\.tests\.helpers\s+import\s+([^\n\(\)]+)",
        content,
        re.MULTILINE,
    )
    helpers += re.findall(
        r"import\s+" + collection_to_use + r"\.tests\.helpers\.([^\s]+)",
        content,
        re.MULTILINE,
    )
    helpers = list(set(helpers))
    return helpers


def build_artifacts_from_collection(collection_root):
    """Build a list of Artifact objects based on python scripts found in collection.

    Args:
        collection_root (str): The path to the root of the collection

    Returns:
        list[Artifact]: A list of artifacts.
    """
    files = []
    files += get_all_files_in_dir_tree(collection_root + "/plugins/modules")
    files += get_all_files_in_dir_tree(collection_root + "/plugins/module_utils")
    files += get_all_files_in_dir_tree(collection_root + "/tests/unit")
    files += get_all_files_in_dir_tree(collection_root + "/tests/functional")
    files += get_all_files_in_dir_tree(collection_root + "/tests/helpers")
    artifacts = []
    for file in files:
        if file.endswith(".py"):
            artifacts.append(Artifact.from_path(file))
    return artifacts


def get_all_files_in_dir_tree(base_path):
    """Recursively search subdirectories for files.

    Args:
        base_path (str): The directory to recursively search.

    Returns:
        list[str]: A list of file paths.
    """
    found_files = []
    for root, subdirs, files in os.walk(base_path):
        for file in files:
            found_files.append(os.path.join(root, file))
    return found_files


def get_changed_files(path, branch="origin/dev"):
    """Get a list of files changed compared to specified branch.
    Deleted files are not included.

    Args:
        branch (str, optional): The branch to compare to. Defaults to "dev".

    Raises:
        RuntimeError: When git diff fails.

    Returns:
        list[str]: A list of changed file paths.
    """
    changed_files = []
    get_diff = subprocess.Popen(
        ["git", "diff", "--name-status", branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path,
    )
    stdout, stderr = get_diff.communicate()
    stdout = stdout.decode("utf-8")
    if get_diff.returncode > 0:
        raise RuntimeError("Could not acquire change list")
    if stdout:
        changed_files = [
            x.split("\t")[-1] for x in stdout.split("\n") if "D" not in x.split("\t")[0]
        ]
    return changed_files


def parse_arguments():
    """Parse and return command line arguments.

    Returns:
        Args: The populated namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        default=os.getcwd(),
        help="The root directory of the Ansible collection. Defaults to CWD.",
    )
    parser.add_argument(
        "-b",
        "--branch",
        default="origin/dev",
        help="The branch to compare current branch with. Used to determine changed files.",
    )
    parser.add_argument(
        "-c",
        "--collection",
        default="ibm_zos_core",
        help="The collection name.",
    )
    parser.add_argument(
        "-s",
        "--skip",
        required=False,
        help="A list of test name patterns to skip. Separate with spaces.",
    )
    parser.add_argument(
        "-l",
        "--long",
        action="store_true",
        help="Print one test per line to stdout. Default behavior prints all tests on same line.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    # TODO: add logic to only grab necessary tests that are impacted by changes
    args = parse_arguments()

    global collection_to_use
    collection_to_use = args.collection

    artifacts = build_artifacts_from_collection(args.path)
    all_artifact_manager = ArtifactManager(artifacts)

    changed_files = get_changed_files(args.path, args.branch)

    changed_artifacts = []
    for file in changed_files:
        found_artifact = all_artifact_manager.get_from_path(file)
        if found_artifact:
            changed_artifacts.append(found_artifact)

    changed_artifact_manager = ArtifactManager(changed_artifacts)

    modules_to_test = all_artifact_manager.get_artifacts_with_dependency(
        changed_artifact_manager.get_artifacts_with_matching_source("module_util"),
        "module",
    )

    modules_to_test = (
        modules_to_test
        + changed_artifact_manager.get_artifacts_with_matching_source("module")
    )

    modules_to_test = list(set(modules_to_test))

    helpers_to_consider = all_artifact_manager.get_artifacts_with_dependency(
        modules_to_test,
        "helper",
    )

    tests_to_run = all_artifact_manager.get_artifacts_with_dependency(
        modules_to_test, "test"
    )

    tests_to_run += all_artifact_manager.get_artifacts_with_dependency(
        helpers_to_consider, "test"
    )

    tests_to_run = (
        tests_to_run
        + changed_artifact_manager.get_artifacts_with_matching_source("test")
    )

    tests_to_run = list(set(tests_to_run))

    skip_pattern = ""
    if args.skip:
        to_skip = re.split(r"\s+", args.skip.strip())
        for pattern in to_skip:
            skip_pattern += "(?:{0})|".format(pattern)
        skip_pattern = skip_pattern.rstrip("|")

    if args.long:
        for test in tests_to_run:
            if not skip_pattern or not re.search(
                skip_pattern, test.path, re.IGNORECASE
            ):
                print(test.path)
    else:
        to_print = ""
        for test in tests_to_run:
            if not skip_pattern or not re.search(
                skip_pattern, test.path, re.IGNORECASE
            ):
                to_print += test.path + " "
        if to_print:
            print(to_print.rstrip())
