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
from ansible.utils.display import Display

# ------------------------------
# Mock zoautil_py and zsystem
# ------------------------------
sys.modules['zoautil_py'] = MagicMock()
sys.modules['zoautil_py.zsystem'] = MagicMock()

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
# Tests
# ------------------------------
def test_python_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 14))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.14.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency check passed with warnings" in exc.value.value["msg"]
    assert any("Python 3.14.0 exceeds the maximum tested version" in w for w in exc.value.value["warnings"])

def test_zos_above_max(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "3.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency check passed with warnings" in exc.value.value["msg"]
    assert any("z/OS 3.5 exceeds the maximum tested version" in w for w in exc.value.value["warnings"])

def test_zos_fetch_failure(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: None)
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"] or \
           "Dependency check passed with warnings" in exc.value.value["msg"]

def test_python_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 10))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.10.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible Python version" in str(exc.value)

def test_zos_below_min(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.4")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Incompatible z/OS version" in str(exc.value)

def test_versions_within_range(monkeypatch):
    monkeypatch.setattr(dependency_checker, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dependency_checker, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dependency_checker, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dependency_checker, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dependency_checker.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]
