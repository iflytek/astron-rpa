import ast
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.schemas.desktop_ui import DESKTOP_COMPONENT_OPERATIONS, DESKTOP_OPERATIONS
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services.desktop_ui import freeze_desktop, validate_desktop_review
from app.services.execution import ExecutionService
from app.services.integration_policy import require_admission, workflow_profile
from tests.test_integration_policy import policy  # noqa: F401
from tests.test_office_file import files  # noqa: F401
from tests.test_workflow_control import AsyncSessionAdapter, database  # noqa: F401


def declaration():
    return {
        "capabilityClass": "desktop-ui",
        "capabilities": ["desktop-ui"],
        "componentOperations": ["Window.exist"],
        "requiresGui": True,
        "requiresHuman": False,
        "exclusiveTerminal": True,
        "risk": "medium",
        "sideEffects": ["desktop-interaction"],
        "fileInputs": False,
        "fileOutputs": False,
        "fileContract": None,
        "allowedTransports": ["mcp", "rest"],
        "desktopContract": {
            "version": 1,
            "resolution": {"width": 1920, "height": 1080},
            "programs": ["editor"],
            "humanMode": "none",
        },
        "desktopReview": {
            "version": 1,
            "operations": ["Window.exist"],
            "programs": {"editor": "C:/Apps/editor.exe"},
            "targets": ["Reviewed target"],
            "boundedResources": True,
            "noHighRiskActions": True,
            "inputBindingsReviewed": True,
            "resourcesReleased": True,
        },
    }


def test_bound_private_review_and_transports(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    values = declaration()
    policy(workflow, **values)
    profile = workflow_profile(workflow, "owner")
    assert profile["admission"]["allowed"]
    assert "desktopReview" not in profile
    assert "C:/Apps" not in json.dumps(profile)
    assert freeze_desktop(profile, 60)["programPaths"] == values["desktopReview"]["programs"]
    for transport in ("mcp", "rest"):
        require_admission(workflow, "owner", profile["revision"], transport=transport)
    values["desktopReview"]["targets"] = ["New target"]
    policy(workflow, **values)
    with pytest.raises(WorkflowAccessError) as error:
        freeze_desktop(profile, 60)
    assert error.value.code == "PROFILE_STALE"


@pytest.mark.parametrize("timeout", [None, 0, 3601, True])
def test_desktop_needs_finite_deadline(timeout):
    with pytest.raises(WorkflowAccessError) as error:
        freeze_desktop({}, timeout)
    assert error.value.code == "DESKTOP_EXECUTION_DEADLINE_REQUIRED"


@pytest.mark.parametrize(
    "changes",
    [
        {"requiresGui": False},
        {"exclusiveTerminal": False},
        {"requiresHuman": True},
        {"risk": "high"},
        {"allowedTransports": []},
        {"sideEffects": []},
        {"fileInputs": True},
        {"componentOperations": ["Software.cmd"]},
        {"componentOperations": ["Software.close"]},
        {"componentOperations": ["BrowserSoftware.browser_close"]},
        {"componentOperations": ["ComputerUse.run"]},
        {"componentOperations": ["System.screen_unlock"]},
        {"componentOperations": ["WinEle.screenshot_element"]},
        {"componentOperations": ["Dialog.input_box"]},
        {"desktopReview": {}},
        {"desktopContract": {}},
    ],
)
def test_rejects_unsafe_or_incomplete_declarations(changes):
    values = declaration()
    values.update(changes)
    with pytest.raises(WorkflowAccessError):
        validate_desktop_review(SimpleNamespace(**values))


def test_attended_dialog_and_reviewed_programs():
    values = declaration()
    values["componentOperations"] = ["Dialog.input_box"]
    values["desktopReview"]["operations"] = ["Dialog.input_box"]
    values["requiresHuman"] = True
    values["desktopContract"]["humanMode"] = "attended"
    validate_desktop_review(SimpleNamespace(**values))
    for path in ("editor.exe", "C:/Apps/../cmd.exe", "//server/share/program.exe", "C:/Apps/run.cmd"):
        bad = deepcopy(values)
        bad["desktopReview"]["programs"]["editor"] = path
        with pytest.raises(WorkflowAccessError):
            validate_desktop_review(SimpleNamespace(**bad))


def test_operations_exist_in_components():
    root = Path(__file__).resolve().parents[3] / "engine/components"
    for component, operations in DESKTOP_COMPONENT_OPERATIONS.items():
        actual = set()
        for path in (root / f"astronverse-{component}" / "src").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
                actual.update(
                    f"{cls.name}.{node.name}"
                    for node in cls.body
                    if isinstance(node, ast.FunctionDef)
                    and any("atomicMg.atomic" in ast.unparse(d) for d in node.decorator_list)
                )
        assert operations <= actual
    assert not any(op.startswith(("ComputerUse.", "VerifyCode.", "BrowserScript.")) for op in DESKTOP_OPERATIONS)


def test_desktop_screenshot_requires_both_private_reviews(policy, files):
    from app.services.integration_files import FILE_LIMITS

    workflow = Workflow(
        project_id="p",
        user_id="owner",
        version=1,
        parameters=json.dumps({"type": "object", "properties": {"target": {"type": "string"}}}),
    )
    values = declaration()
    operations = ["Window.top", "System.screen_shot"]
    values.update(
        componentOperations=operations,
        fileOutputs=True,
        sideEffects=["desktop-interaction", "workspace-files"],
        fileContract={"version": 1, "limits": FILE_LIMITS, "inputs": {}, "outputs": {"target": "screen.png"}},
        fileReview={
            "version": 1,
            "workspaceOnly": True,
            "macrosDisabled": True,
            "externalServicesReviewed": True,
            "boundedResources": True,
            "resourcesReleased": True,
            "operations": operations,
        },
    )
    values["desktopReview"]["operations"] = operations
    policy(workflow, **values)
    profile = workflow_profile(workflow, "owner")
    assert profile["admission"]["allowed"]
    require_admission(workflow, "owner", profile["revision"], params={"target": "output:target"})
    with pytest.raises(WorkflowAccessError):
        require_admission(workflow, "owner", profile["revision"], params={"target": "C:/outside.png"})
    for field in ("desktopReview", "fileReview"):
        invalid = deepcopy(values)
        invalid[field] = None
        policy(workflow, **invalid)
        assert not workflow_profile(workflow, "owner")["admission"]["allowed"]


@pytest.mark.asyncio
async def test_freezes_private_environment_and_rejects_old_client(database, policy, monkeypatch):
    capability = {"protocol": 1, "clientId": "client", "supportsCancel": True}
    monkeypatch.setattr("app.services.execution.management.capabilities", AsyncMock(return_value=capability))
    with Session(database) as db:
        workflow = db.get(Workflow, "allowed")
        values = declaration()
        policy(workflow, **values)
        service = ExecutionService(AsyncSessionAdapter(db))
        service.execute_workflow = AsyncMock()
        request = ExecutionCreate(
            project_id="allowed", version=2, params={}, execution_timeout=60, capability_class="desktop-ui"
        )
        with pytest.raises(WorkflowAccessError) as error:
            await service.execute_authorized_workflow(request, "owner", wait=False)
        assert error.value.code == "CLIENT_DESKTOP_PROTOCOL_UNSUPPORTED"
        service.execute_workflow.assert_not_awaited()
        capability["desktopProtocolVersion"] = 1
        await service.execute_authorized_workflow(request, "owner", wait=False)
        frozen = json.loads(service.execute_workflow.await_args.kwargs["metadata"]["data_contract"])
        assert frozen["limits"]["maxBytes"] == 1048576
        assert frozen["desktopContract"]["programPaths"] == values["desktopReview"]["programs"]
        assert frozen["desktopContract"]["targets"] == values["desktopReview"]["targets"]
