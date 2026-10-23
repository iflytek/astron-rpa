from copy import deepcopy

import pytest
from astronverse.scheduler.core.executor import managed_desktop as desktop


@pytest.fixture
def environment(tmp_path, monkeypatch):
    program = tmp_path / "app.exe"
    program.write_bytes(b"fixture")
    contract = {
        "version": 1,
        "resolution": {"width": 1920, "height": 1080},
        "programs": ["app"],
        "programPaths": {"app": str(program)},
        "targets": ["Target", "Expected dialog"],
        "humanMode": "none",
    }
    state = {"session": 1, "resolution": contract["resolution"].copy(), "windows": []}
    monkeypatch.setattr(desktop, "probe", lambda: deepcopy(state))
    return contract, state


def test_guard_validates_installed_software_without_launch(environment):
    contract, _ = environment
    guard = desktop.DesktopGuard(contract)
    guard.check(initial=True)
    guard.check()
    contract["programPaths"]["app"] += ".missing"
    with pytest.raises(desktop.DesktopError, match="DESKTOP_SOFTWARE_UNAVAILABLE"):
        desktop.DesktopGuard(contract).check(initial=True)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("session", 2, "DESKTOP_SESSION_CHANGED"),
        ("resolution", {"width": 800, "height": 600}, "DESKTOP_RESOLUTION_MISMATCH"),
        ("windows", [{"title": "Target", "popup": "Unexpected"}], "DESKTOP_POPUP_BLOCKED"),
    ],
)
def test_guard_rechecks_environment(environment, field, value, code):
    contract, state = environment
    guard = desktop.DesktopGuard(contract)
    guard.check(initial=True)
    state[field] = value
    with pytest.raises(desktop.DesktopError, match=code):
        guard.check()


def test_expected_dialog_and_unrelated_windows_do_not_block(environment):
    contract, state = environment
    state["windows"] = [{"title": "Target", "popup": "Expected dialog"}, {"title": "Other app", "popup": "Unrelated"}]
    desktop.DesktopGuard(contract).check(initial=True)


@pytest.mark.parametrize("contract", [None, {}, {"version": True}, {"version": 1, "resolution": []}])
def test_invalid_client_contract_rejected(contract):
    with pytest.raises(desktop.DesktopError, match="DESKTOP_CONTRACT_INVALID"):
        desktop.DesktopGuard(contract)
