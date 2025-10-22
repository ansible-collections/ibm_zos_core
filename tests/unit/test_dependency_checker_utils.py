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
# Helper to mock display.warning
# ------------------------------
def capture_warnings(monkeypatch):
    warnings_called = []
    monkeypatch.setattr(dependency_checker.display, "warning", lambda msg: warnings_called.append(msg))
    return warnings_called

# ------------------------------
# Test: Python above max triggers warning
# ------------------------------
def test_python_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 14))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.14.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    warnings_called = capture_warnings(monkeypatch)

    mod = FakeModule()
    with pytest.raises(StopIteration):
        dependency_checker.validate_dependencies(mod)

    assert any("Python 3.14.0 exceeds the maximum supported version" in w for w in warnings_called)

# ------------------------------
# Test: z/OS above max triggers warning
# ------------------------------
def test_zos_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "3.2")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    warnings_called = capture_warnings(monkeypatch)

    mod = FakeModule()
    with pytest.raises(StopIteration):
        dependency_checker.validate_dependencies(mod)

    assert any("z/OS 3.2 exceeds the maximum supported version" in w for w in warnings_called)

# ------------------------------
# Test: z/OS fetch failure triggers warning
# ------------------------------
def test_zos_fetch_failure(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: None)  # simulate failure
    monkeypatch.setattr(version, "__version__", "2.0.0")

    warnings_called = capture_warnings(monkeypatch)

    mod = FakeModule()
    with pytest.raises(StopIteration):
        dependency_checker.validate_dependencies(mod)

    assert any("Unable to fetch z/OS version" in w for w in warnings_called)

# ------------------------------
# Test: Python below min triggers fail
# ------------------------------
def test_python_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 10))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.10.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible Python version" in str(exc.value)

# ------------------------------
# Test: Versions within range → no warning
# ------------------------------
def test_versions_within_range(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    warnings_called = capture_warnings(monkeypatch)

    mod = FakeModule()
    with pytest.raises(StopIteration):
        dependency_checker.validate_dependencies(mod)

    assert len(warnings_called) == 0
