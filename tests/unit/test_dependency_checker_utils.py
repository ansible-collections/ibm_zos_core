# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import pytest
from unittest.mock import MagicMock

# ------------------------------
# Mock zoautil_py and zsystem
# ------------------------------
sys.modules['zoautil_py'] = MagicMock()
sys.modules['zoautil_py.zsystem'] = MagicMock()

# Import modules after mocking
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version

# ------------------------------
# FakeModule for testing
# ------------------------------
class FakeModule:
    def run_command(self, cmd):
        return 0, "", ""

    def fail_json(self, **kwargs):
        raise Exception(kwargs.get("msg", "fail_json called"))

    def exit_json(self, **kwargs):
        raise StopIteration(kwargs)

# ------------------------------
# Test: Success for Python in range
# ------------------------------
def test_validate_dependencies_success(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]

# ------------------------------
# Test: Success for Python upper bound (3.13)
# ------------------------------
def test_validate_dependencies_python_upper(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 13))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.13.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]

# ------------------------------
# Test: Python out-of-range (>3.13)
# ------------------------------
def test_validate_dependencies_python_out_of_range(monkeypatch):
    # Use pytest's monkeypatch fixture to temporarily override functions
    # in dependency_checker and version modules. This simulates different
    # Python, z/OS, and ZOAU versions for testing without changing the real environment.
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 14))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.14.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)
    assert "expected 3.12-3.13" in str(exc.value)

# ------------------------------
# Test: z/OS version out-of-range
# ------------------------------
def test_validate_dependencies_zos_out_of_range(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.4")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)

# ------------------------------
# Test: ZOAU version mismatch
# ------------------------------
def test_validate_dependencies_zoau_mismatch(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.3.9")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)
