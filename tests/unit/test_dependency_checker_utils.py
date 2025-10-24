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
from unittest.mock import patch
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version


class FakeModule:
    def __init__(self):
        self.warned = []
        self.failed = None
        self.exited = None

    def fail_json(self, **kwargs):
        self.failed = kwargs.get("msg")
        raise Exception(kwargs.get("msg", "fail_json called"))

    def exit_json(self, **kwargs):
        # Should not be called anymore in new behavior
        self.exited = kwargs
        raise Exception("exit_json should not be called")

    def warn(self, msg):
        self.warned.append(msg)


# ------------------------------
# Test: Python above max triggers warning but does not exit
# ------------------------------
def test_python_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 14))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.14.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)

    assert any("Python 3.14.0 exceeds the maximum tested version" in w for w in mod.warned)
    assert "Dependency check completed with warnings." in mod.warned


# ------------------------------
# Test: z/OS above max triggers warning
# ------------------------------
def test_zos_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "3.2")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)

    assert any("z/OS 3.2 exceeds the maximum tested version" in w for w in mod.warned)
    assert "Dependency check completed with warnings." in mod.warned


# ------------------------------
# Test: versions within range pass without warnings
# ------------------------------
def test_versions_within_range(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)

    assert mod.warned == ["Dependency compatibility check passed."]


# ------------------------------
# Test: Python below min triggers warning
# ------------------------------
def test_python_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 11))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.11.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)

    assert any("Python 3.11.0 is below the minimum tested version" in w for w in mod.warned)
    assert "Dependency check completed with warnings." in mod.warned


# ------------------------------
# Test: z/OS below min triggers warning
# ------------------------------
def test_zos_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.4")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    dependency_checker.validate_dependencies(mod)

    assert any("z/OS 2.4 is below the minimum tested version" in w for w in mod.warned)
    assert "Dependency check completed with warnings." in mod.warned


# ------------------------------
# Test: ZOAU below minimum version triggers failure
# ------------------------------
def test_zoau_below_min_fails_mwndm(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.3.9")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible ZOAU version" in str(exc.value)

