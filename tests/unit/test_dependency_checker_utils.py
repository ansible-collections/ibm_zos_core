# import pytest
# from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker as dc
# from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import versions

# # ------------------------------
# # FakeModule for testing
# # ------------------------------
# class FakeModule:
#     def run_command(self, cmd):
#         return 0, "", ""

#     def fail_json(self, **kwargs):
#         raise Exception(kwargs.get("msg", "fail_json called"))

#     def exit_json(self, **kwargs):
#         raise StopIteration(kwargs)

# # ------------------------------
# # Test Success
# # ------------------------------
# def test_validate_dependencies_success(monkeypatch):
#     # Monkeypatch fetchers to match compatibility matrix
#     monkeypatch.setattr(dc, "get_zoau_version", lambda mod: "1.4.0")
#     monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
#     monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
#     monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.5")
#     monkeypatch.setattr(versions, "__version__", "2.0.0")

#     mod = FakeModule()
#     with pytest.raises(StopIteration) as exc:
#         dc.validate_dependencies(mod)
#     assert "Dependency compatibility check passed" in exc.value.value["msg"]

# # ------------------------------
# # Test Failure
# # ------------------------------
# def test_validate_dependencies_failure(monkeypatch):
#     monkeypatch.setattr(dc, "get_zoau_version", lambda mod: "9.9.9")
#     monkeypatch.setattr(dc, "get_python_version_info", lambda: (9, 9))
#     monkeypatch.setattr(dc, "get_python_version", lambda: "9.9.9")
#     monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "9.9")
#     monkeypatch.setattr(versions, "__version__", "2.0.0")

#     mod = FakeModule()
#     with pytest.raises(Exception) as exc:
#         dc.validate_dependencies(mod)
#     assert "Incompatible configuration detected" in str(exc.value)
# tests/unit/test_dependency_checker.py
import sys
import pytest
from unittest.mock import MagicMock

# ------------------------------
# Mock zoautil_py and zsystem
# ------------------------------
sys.modules['zoautil_py'] = MagicMock()
sys.modules['zoautil_py.zsystem'] = MagicMock()

# Import your modules after mocking
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
# Test Success
# ------------------------------
def test_validate_dependencies_success(monkeypatch):
    # Monkeypatch fetchers to match compatibility matrix
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "1.4.0")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "2.5")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(StopIteration) as exc:
        dc.validate_dependencies(mod)
    assert "Dependency compatibility check passed" in exc.value.value["msg"]

# ------------------------------
# Test Failure
# ------------------------------
def test_validate_dependencies_failure(monkeypatch):
    # Monkeypatch fetchers to return incompatible versions
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod=None: "9.9.9")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (9, 9))
    monkeypatch.setattr(dc, "get_python_version", lambda: "9.9.9")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod=None: "9.9")
    monkeypatch.setattr(version, "__version__", "2.0.0")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dc.validate_dependencies(mod)
    assert "Incompatible configuration detected" in str(exc.value)
