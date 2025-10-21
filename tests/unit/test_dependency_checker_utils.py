import sys
import pytest
from unittest.mock import MagicMock

# ------------------------------
# Mock zoautil_py and zsystem
# ------------------------------
sys.modules['zoautil_py'] = MagicMock()
sys.modules['zoautil_py.zsystem'] = MagicMock()

# Import modules after mocking
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker as dc
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
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dc.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]

# ------------------------------
# Test: Success for Python upper bound (3.13)
# ------------------------------
def test_validate_dependencies_python_upper(monkeypatch):
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 13))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.13.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dc.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]

# ------------------------------
# Test: Python out-of-range (>3.13)
# ------------------------------
def test_validate_dependencies_python_out_of_range(monkeypatch):
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 14))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.14.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dc.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)
    assert "expected 3.12-3.13" in str(exc.value)

# ------------------------------
# Test: z/OS version out-of-range
# ------------------------------
def test_validate_dependencies_zos_out_of_range(monkeypatch):
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.4.2")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.4")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dc.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)

# ------------------------------
# Test: ZOAU version mismatch
# ------------------------------
def test_validate_dependencies_zoau_mismatch(monkeypatch):
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.3.9")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.6")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dc.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)
