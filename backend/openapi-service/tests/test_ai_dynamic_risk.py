import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services.ai_dynamic_risk import RISK_CONTRACT, freeze_risk, validate_risk_review
from app.services.execution import ExecutionService
from app.services.execution_management import digest

hash_key = digest
from app.services.integration_policy import workflow_profile
from tests.test_execution_management import store  # noqa: F401
from tests.test_integration_policy import policy  # noqa: F401
from tests.test_workflow_control import AsyncSessionAdapter, database  # noqa: F401


def declaration(params=None, key="approved-request"):
    now = int(time.time())
    return {
        "capabilityClass": "ai-dynamic-risk",
        "capabilities": ["ai-dynamic-risk"],
        "componentOperations": ["ChatAI.single_turn_chat"],
        "risk": "medium",
        "requiresGui": False,
        "requiresHuman": False,
        "exclusiveTerminal": True,
        "fileInputs": False,
        "fileOutputs": False,
        "fileContract": None,
        "desktopContract": None,
        "outputSchema": {"type": "object", "properties": {"answer": {"type": "string"}}, "additionalProperties": False},
        "sideEffects": ["external-service"],
        "allowedTransports": ["mcp", "rest"],
        "riskContract": RISK_CONTRACT.copy(),
        "riskReview": {
            "version": 1,
            "trustedRelease": True,
            "sensitiveDataReviewed": True,
            "destinationsReviewed": True,
            "resourcesReleased": True,
            "maxOperations": 5,
            "operations": {"ChatAI.single_turn_chat": {"risk": "medium", "argumentHashes": []}},
            "codeHashes": [],
            "approvals": [
                {
                    "id": "approval-1",
                    "approvedBy": "administrator",
                    "paramsHash": digest(params or {}),
                    "keyHash": hash_key(key),
                    "executionTimeout": 60,
                    "issuedAt": now - 5,
                    "expiresAt": now + 600,
                }
            ],
        },
    }


def test_private_approval_and_frozen_audit(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    values = declaration()
    policy(workflow, **values)
    profile = workflow_profile(workflow, "owner")
    assert profile["admission"]["allowed"]
    assert "riskReview" not in profile
    assert "administrator" not in json.dumps(profile)
    frozen = freeze_risk(profile, "owner", {}, hash_key("approved-request"), 60)
    assert frozen["approval"]["id"] == "approval-1"
    values["riskReview"]["maxOperations"] = 6
    policy(workflow, **values)
    with pytest.raises(WorkflowAccessError) as error:
        freeze_risk(profile, "owner", {}, hash_key("approved-request"), 60)
    assert error.value.code == "PROFILE_STALE"


@pytest.mark.parametrize(
    "change",
    [
        {"user": "other"},
        {"params": {"extra": 1}},
        {"key": "unapproved"},
        {"key": None},
        {"timeout": 61},
        {"timeout": 0},
        {"timeout": None},
        {"expired": True},
        {"future": True},
    ],
)
def test_request_approval_cannot_be_reused_for_changed_request(policy, change):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    values = declaration()
    approval = values["riskReview"]["approvals"][0]
    if change.get("expired"):
        approval.update(issuedAt=int(time.time()) - 120, expiresAt=int(time.time()) - 1)
    if change.get("future"):
        approval.update(issuedAt=int(time.time()) + 120, expiresAt=int(time.time()) + 240)
    policy(workflow, **values)
    profile = workflow_profile(workflow, "owner")
    key = change.get("key", "approved-request")
    with pytest.raises(WorkflowAccessError):
        freeze_risk(
            profile,
            change.get("user", "owner"),
            change.get("params", {}),
            hash_key(key) if key else None,
            change.get("timeout", 60),
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"risk": "low"},
        {"riskReview": {}},
        {"outputSchema": None},
        {"allowedTransports": []},
        {"requiresHuman": True},
        {"requiresGui": True},
        {"fileInputs": True},
        {"componentOperations": ["ComputerUse.run"]},
        {"componentOperations": ["System.screen_unlock"]},
        {"riskContract": {**RISK_CONTRACT, "automaticExecution": True}},
    ],
)
def test_incomplete_or_autonomous_declarations_are_denied(changes):
    values = declaration()
    values.update(changes)
    with pytest.raises(WorkflowAccessError):
        validate_risk_review(SimpleNamespace(**values))


def test_code_and_irreversible_operations_require_argument_audit():
    values = declaration()
    values.update(componentOperations=["Smart.run_code"], risk="high", sideEffects=["dynamic-code"])
    review = values["riskReview"]
    review["operations"] = {"Smart.run_code": {"risk": "high", "argumentHashes": []}}
    review["codeHashes"] = ["a" * 64]
    with pytest.raises(WorkflowAccessError):
        validate_risk_review(SimpleNamespace(**values))
    review["operations"]["Smart.run_code"]["argumentHashes"] = ["b" * 64]
    validate_risk_review(SimpleNamespace(**values))
    review["codeHashes"] = []
    with pytest.raises(WorkflowAccessError):
        validate_risk_review(SimpleNamespace(**values))


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["mcp", "rest"])
async def test_admission_before_dispatch_and_client_protocol(database, policy, monkeypatch, transport):
    capability = {"protocol": 1, "clientId": "client", "supportsCancel": True}
    monkeypatch.setattr("app.services.execution.management.capabilities", AsyncMock(return_value=capability))
    with Session(database) as db:
        workflow = db.get(Workflow, "allowed")
        policy(workflow, **declaration())
        service = ExecutionService(AsyncSessionAdapter(db))
        service.execute_workflow = AsyncMock()
        request = ExecutionCreate(
            project_id="allowed", version=2, params={}, execution_timeout=60, idempotency_key="approved-request"
        )
        with pytest.raises(WorkflowAccessError) as error:
            await service.execute_authorized_workflow(request, "owner", wait=False, transport=transport)
        assert error.value.code == "CLIENT_RISK_PROTOCOL_UNSUPPORTED"
        service.execute_workflow.assert_not_awaited()
        capability["riskProtocolVersion"] = 1
        await service.execute_authorized_workflow(request, "owner", wait=False, transport=transport)
        frozen = json.loads(service.execute_workflow.await_args.kwargs["metadata"]["data_contract"])
        assert frozen["riskContract"]["approval"]["id"] == "approval-1"
        assert frozen["limits"]["maxBytes"] == 1048576


@pytest.mark.asyncio
async def test_high_risk_not_advertised_as_automatic_dynamic_tool(policy):
    from app.services.streamable_mcp import ToolsConfig

    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]", name="Approved workflow")
    policy(workflow, **declaration())
    config = ToolsConfig()
    config.get_user_workflows = AsyncMock(return_value=[workflow.to_dict()])
    assert await config.get_tools_for_user("owner") == []


@pytest.mark.asyncio
async def test_approved_replay_survives_revocation_without_dispatch(store, policy, monkeypatch):
    from app.services.execution import _execution_tasks

    engine, factory = store
    with Session(engine) as db:
        workflow = db.get(Workflow, "project")
        values = declaration({"value": 0})
        policy(workflow, **values)
        revision = workflow_profile(workflow, "owner")["revision"]
    probe = AsyncMock(return_value={"protocol": 1, "clientId": "client", "riskProtocolVersion": 1})
    monkeypatch.setattr("app.services.execution.management.capabilities", probe)
    request = ExecutionCreate(
        project_id="project",
        version=1,
        params={"value": 0},
        idempotency_key="approved-request",
        execution_timeout=60,
        profile_revision=revision,
    )
    async with factory() as db:
        first = await ExecutionService(db).execute_authorized_workflow(request, "owner", wait=False, transport="mcp")
    values["riskReview"]["approvals"] = []
    policy(workflow, **values)
    probe.reset_mock()
    async with factory() as db:
        again = await ExecutionService(db).execute_authorized_workflow(request, "owner", wait=False, transport="rest")
        assert again.id == first.id
        with pytest.raises(WorkflowAccessError):
            await ExecutionService(db).execute_authorized_workflow(
                request.model_copy(update={"params": {"value": 1}}), "owner", wait=False
            )
    probe.assert_not_awaited()
    await asyncio.gather(*list(_execution_tasks))


def test_risk_does_not_bypass_file_or_desktop_contracts():
    for operation in ("File.file_write", "Window.top", "BrowserScript.js_run", "System.screen_shot"):
        values = declaration()
        values["componentOperations"].append(operation)
        values["riskReview"]["operations"][operation] = {"risk": "high", "argumentHashes": ["a" * 64]}
        values["risk"] = "high"
        values["sideEffects"] = ["dynamic-code", "desktop-interaction"]
        with pytest.raises(WorkflowAccessError):
            validate_risk_review(SimpleNamespace(**values))


def test_risk_inventory_matches_real_atomic_keys():
    import ast
    from pathlib import Path

    from app.schemas.ai_dynamic_risk import RISK_COMPONENT_OPERATIONS

    root = Path(__file__).resolve().parents[3] / "engine/components"
    for component, expected in RISK_COMPONENT_OPERATIONS.items():
        actual = set()
        for path in (root / ("astronverse-" + component) / "src").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and ast.unparse(decorator.func) == "atomicMg.atomic"
                        and decorator.args
                    ):
                        actual.add(ast.literal_eval(decorator.args[0]) + "." + node.name)
        assert expected <= actual, (component, expected - actual)
