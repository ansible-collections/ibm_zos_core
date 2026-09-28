# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger


class FakeModule:
    def __init__(self):
        self.warned = []

    def fail_json(self, **kwargs):
        raise Exception(kwargs.get("msg", "fail_json called"))

    def warn(self, msg):
        self.warned.append(msg)


# ------------------------------------------------------------------------------
# Common fixture to silence logging during tests
# ------------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    logger_instance = SingletonLogger().get_logger(verbosity=3)
    monkeypatch.setattr(logger_instance, "debug", lambda *a, **kw: None)
    monkeypatch.setattr(logger_instance, "warning", lambda *a, **kw: None)
    monkeypatch.setattr(logger_instance, "error", lambda *a, **kw: None)
    yield

# ------------------------------
# Test: versions within range pass without warning
# ------------------------------
def test_versions_within_range(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version_str", lambda: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_str", lambda: "3.12")
    monkeypatch.setattr(dependency_checker, "get_zos_version_str", lambda mod: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)
    assert mod.warned == []


# ------------------------------
# Test: Python wrong major version triggers warning
# ------------------------------
def test_python_wrong_major(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version_str", lambda: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_str", lambda: "2.7")
    monkeypatch.setattr(dependency_checker, "get_zos_version_str", lambda mod: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)
    assert any("Incompatible Python version 2.7" in w for w in mod.warned)


# ------------------------------
# Test: z/OS below min triggers warning
# ------------------------------
def test_zos_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version_str", lambda: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_str", lambda: "3.12")
    monkeypatch.setattr(dependency_checker, "get_zos_version_str", lambda mod: "2.4")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)
    assert any("Incompatible z/OS version 2.4" in w for w in mod.warned)


# ------------------------------
# Test: ZOAU below minimum version triggers warning
# ------------------------------
def test_zoau_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version_str", lambda: "1.3.5")
    monkeypatch.setattr(dependency_checker, "get_python_version_str", lambda: "3.12")
    monkeypatch.setattr(dependency_checker, "get_zos_version_str", lambda mod: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)
    assert any("Incompatible ZOAU version 1.3.5" in w for w in mod.warned)
