import pytest
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import dependency_checker as dc

class FakeModule:
    def run_command(self, cmd):
        return 0, "", ""

    def fail_json(self, **kwargs):
        raise Exception(kwargs.get("msg", "fail_json called"))

    def exit_json(self, **kwargs):
        # Instead of StopIteration, store the result so we can inspect it
        self.result = kwargs
        raise SystemExit  # This simulates Ansible stopping execution

def test_validate_dependencies_success(monkeypatch):
    # Monkeypatch fetchers to match the compatibility matrix exactly
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod: "1.3.5")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod: "2.5")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (3, 12))
    monkeypatch.setattr(dc, "get_python_version", lambda: "3.12.0")
    monkeypatch.setattr(dc, "get_galaxy_core_version", lambda: "1.12.0")

    mod = FakeModule()
    try:
        dc.validate_dependencies(mod)
    except SystemExit:
        # Capture the message from exit_json
        print("Message:", mod.result["msg"])
        assert "Dependency compatibility check passed" in mod.result["msg"]

def test_validate_dependencies_failure(monkeypatch):
    monkeypatch.setattr(dc, "get_zoau_version", lambda mod: "9.9.9")
    monkeypatch.setattr(dc, "get_zos_version", lambda mod: "9.9")
    monkeypatch.setattr(dc, "get_python_version_info", lambda: (9, 9))
    monkeypatch.setattr(dc, "get_python_version", lambda: "9.9.9")
    monkeypatch.setattr(dc, "get_galaxy_core_version", lambda: "9.9.9")

    mod = FakeModule()
    with pytest.raises(Exception) as exc:
        dc.validate_dependencies(mod)
    print("Failure message:", str(exc.value))
    assert "Incompatible configuration detected" in str(exc.value)
