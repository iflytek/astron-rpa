"""Service workflow boundaries and shared MCP/REST result semantics."""

import json
from copy import deepcopy
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.dependencies import get_execution_service, get_user_id_from_api_key
from app.models.workflow import Execution, Workflow
from app.routers import executions, workflows
from app.schemas.integration import SERVICE_READ_OPERATIONS
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution import ExecutionService
from app.services.integration_policy import require_admission, workflow_profile
from app.services.service_read import RULES, validate_read_review
from app.services.workflow_control import WorkflowControlService
from tests.test_integration_policy import policy  # noqa: F401
from tests.test_workflow_control import AsyncSessionAdapter, database  # noqa: F401


def review(operations):
    return {
        "version": 1,
        "boundedResources": True,
        "readOnlyConnections": True,
        "operationInputs": {
            operation: {
                name: values[0] if values is not None else "SELECT 42 AS answer"
                for name, values in RULES.get(operation, {}).items()
            }
            for operation in operations
        },
    }


@pytest.mark.parametrize(("capability", "operations"), SERVICE_READ_OPERATIONS.items())
def test_every_supported_operation_has_a_reviewed_admission(policy, capability, operations):
    if not operations:
        return  # Reserved identifier has no supported operation.
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(
        workflow,
        capabilityClass=capability,
        capabilities=[capability],
        componentOperations=sorted(operations),
        requiresGui=capability == "browser-read",
        readOnlyReview=review(operations),
    )
    profile = require_admission(workflow, "owner", transport="mcp", params={})
    assert profile["readContractVersion"] == 1
    assert "readOnlyReview" not in profile
    with pytest.raises(WorkflowAccessError, match="Transport"):
        require_admission(workflow, "owner", transport="rest", params={})


@pytest.mark.parametrize(
    ("operation", "argument", "value"),
    [
        ("Network.http_request", "request_type", "post"),
        ("Network.http_request", "file_path", "upload.txt"),
        ("Network.http_request", "save_type", "yes"),
        ("Email.receive_email", "mask_as_read_flag", True),
        ("Email.receive_email", "save_attachment_flag", True),
        ("BrowserElement.get_table", "to_excel", True),
        ("BrowserElement.data_batch", "multi_page", True),
        ("BrowserElement.data_batch", "page_count", 2),
        ("BrowserElement.data_batch", "is_save_to_data_table", True),
        ("BrowserElement.element_operation", "operation_type", "set"),
        ("Database.query_sql", "sql", "DELETE FROM records"),
        ("Database.query_sql", "sql", "SELECT 1; DELETE FROM records"),
        ("Database.query_sql", "sql", "SELECT * INTO OUTFILE 'output' FROM records"),
        ("Database.query_sql", "sql", {"parameter": "sql"}),
    ],
)
def test_side_effect_switches_and_dynamic_sql_are_rejected(operation, argument, value):
    declaration = review([operation])
    declaration["operationInputs"][operation][argument] = value
    with pytest.raises(WorkflowAccessError, match="read constraints"):
        validate_read_review(declaration, [operation], {})


def test_bound_arguments_require_safe_schema_and_actual_values():
    operation = "Network.http_request"
    declaration = review([operation])
    declaration["operationInputs"][operation]["request_type"] = {"parameter": "method"}
    schema = {"properties": {"method": {"type": "string", "enum": ["get", "head"]}}}
    validate_read_review(declaration, [operation], schema, {"method": "head"})
    with pytest.raises(WorkflowAccessError):
        validate_read_review(declaration, [operation], schema, {"method": "delete"})
    bad = deepcopy(schema)
    bad["properties"]["method"]["enum"].append("post")
    with pytest.raises(WorkflowAccessError):
        validate_read_review(declaration, [operation], bad)


def test_every_instance_of_an_operation_must_be_reviewed():
    operation = "Network.http_request"
    declaration = review([operation])
    first = declaration["operationInputs"][operation]
    declaration["operationInputs"][operation] = [first, {**first, "request_type": "head"}]
    validate_read_review(declaration, [operation], {})
    declaration["operationInputs"][operation][1]["request_type"] = "post"
    with pytest.raises(WorkflowAccessError):
        validate_read_review(declaration, [operation], {})
    declaration["operationInputs"][operation] = []
    with pytest.raises(WorkflowAccessError):
        validate_read_review(declaration, [operation], {})


@pytest.mark.asyncio
async def test_service_execution_freezes_json_output_and_enforces_transport(database, policy, monkeypatch):
    monkeypatch.setattr(
        "app.services.execution.management.capabilities", AsyncMock(return_value={"clientId": "client"})
    )
    with Session(database) as db:
        workflow = db.get(Workflow, "allowed")
        operations = ["Database.connect_database", "Database.query_sql", "Database.disconnect_database"]
        policy(
            workflow,
            capabilityClass="service-database-read",
            capabilities=["service-database-read"],
            componentOperations=operations,
            readOnlyReview=review(operations),
            outputSchema={"type": "object", "properties": {"answer": {"type": "integer"}}},
        )
        service = ExecutionService(AsyncSessionAdapter(db))
        service.execute_workflow = AsyncMock()
        request = ExecutionCreate(project_id="allowed", version=2, capability_class="service-database-read")
        with pytest.raises(WorkflowAccessError) as exc:
            await service.execute_authorized_workflow(request, "owner", transport="rest")
        assert exc.value.code == "TRANSPORT_NOT_ALLOWED"
        service.execute_workflow.assert_not_awaited()
        await service.execute_authorized_workflow(request, "owner", transport="mcp")
        contract = json.loads(service.execute_workflow.await_args.kwargs["metadata"]["data_contract"])
        assert contract["outputSchema"]["properties"]["answer"] == {"type": "integer"}
        assert contract["limits"]["maxBytes"] == 1_048_576
        old = workflow_profile(workflow, "owner")["revision"]
        changed = review(operations)
        changed["operationInputs"]["Database.query_sql"]["sql"] = "SELECT 43 AS answer"
        policy(
            workflow,
            capabilityClass="service-database-read",
            capabilities=["service-database-read"],
            componentOperations=operations,
            readOnlyReview=changed,
        )
        with pytest.raises(WorkflowAccessError) as exc:
            require_admission(workflow, "owner", old)
        assert exc.value.code == "PROFILE_STALE"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("state", "secrets"),
    [("COMPLETED", None), ("COMPLETED", '["token"]'), ("RUNNING", None), ("TIMEOUT", None), ("UNKNOWN", None)],
)
async def test_rest_routes_return_the_same_authoritative_snapshot_as_mcp(state, secrets):
    record = Execution(
        id="11111111-1111-4111-8111-111111111111",
        project_id="p",
        version=1,
        user_id="owner",
        protocol=1,
        status=state,
        cancel_requested=True,
        cancel_supported=True,
        secret_fields=secrets,
        result=json.dumps({"code": "0000", "data": None if secrets else {"answer": 42}}),
    )
    service = AsyncMock(spec=ExecutionService)
    service.get_authorized_execution.return_value = record
    service.execute_authorized_workflow.return_value = record
    service.request_cancellation.return_value = record
    app = FastAPI()
    app.include_router(executions.router)
    app.include_router(workflows.router)
    app.dependency_overrides[get_execution_service] = lambda: service
    app.dependency_overrides[get_user_id_from_api_key] = lambda: "owner"
    expected = WorkflowControlService.execution_result(record)
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        responses = [
            await client.get(f"/executions/{record.id}?contract=1"),
            await client.post(f"/executions/{record.id}/cancel"),
            await client.post("/workflows/execute-async?contract=1", json={"project_id": "p", "version": 1}),
        ]
    for response in responses:
        assert response.status_code in (200, 202)
        assert response.json()["data"]["snapshot"] == expected


@pytest.mark.asyncio
async def test_rest_contract_preserves_business_errors_and_legacy_error_shape():
    service = AsyncMock(spec=ExecutionService)
    service.execute_authorized_workflow.side_effect = WorkflowAccessError(
        "READ_CONSTRAINT_INVALID", "Workflow read constraints are missing or invalid"
    )
    service.get_authorized_execution.return_value = None
    service.request_cancellation.side_effect = WorkflowAccessError("EXECUTION_NOT_FOUND", "Execution not found")
    app = FastAPI()
    app.include_router(executions.router)
    app.include_router(workflows.router)
    app.dependency_overrides[get_execution_service] = lambda: service
    app.dependency_overrides[get_user_id_from_api_key] = lambda: "owner"
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        denied = await client.post("/workflows/execute-async?contract=1", json={"project_id": "p"})
        legacy = await client.post("/workflows/execute-async", json={"project_id": "p"})
        missing = await client.get("/executions/missing?contract=1")
        cancelled = await client.post("/executions/missing/cancel")
    assert denied.status_code == 403
    assert denied.json()["detail"] == {"code": "READ_CONSTRAINT_INVALID"}
    assert isinstance(legacy.json()["detail"], str)
    for response in (missing, cancelled):
        assert response.status_code == 404
        assert response.json()["detail"] == {"code": "EXECUTION_NOT_FOUND"}
