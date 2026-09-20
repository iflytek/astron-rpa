import json
import os
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.workflow import Execution, Workflow
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution import ExecutionService
from app.services.execution_management import digest
from app.services.integration_policy import Policy, load_policy, require_admission, workflow_profile
from app.services.workflow_control import WorkflowControlService
from app.services.workflow_schema import workflow_input_schema
from tests.test_workflow_control import AsyncSessionAdapter, database  # noqa: F401


@pytest.fixture
def policy(tmp_path, monkeypatch):
    path = tmp_path / "policy.json"
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", str(path))

    def write(workflow, **changes):
        declaration = {
            "userId": "owner",
            "projectId": workflow.project_id,
            "version": workflow.version,
            "revision": "review-1",
            "inputSchemaHash": digest(workflow_input_schema(workflow)),
            "capabilities": ["framework-fixture"],
            "fileInputs": False,
            "fileOutputs": False,
            "requiresGui": False,
            "requiresHuman": False,
            "environment": [],
            "sideEffects": [],
            "risk": "low",
            "executionType": "short",
            "exclusiveTerminal": True,
            "allowed": True,
        }
        declaration.update(changes)
        path.write_text(json.dumps({"schemaVersion": 1, "enforcedUsers": ["owner"], "declarations": [declaration]}))

    return write


def test_profile_unknown_is_not_false_or_admitted(monkeypatch):
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", "")
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    profile = workflow_profile(workflow, "owner")
    assert profile["admission"] == {"allowed": False, "reason": "PROFILE_UNKNOWN", "enforced": False}
    assert profile["requiresGui"] is None
    require_admission(workflow, "owner")  # documented, unenrolled legacy caller
    with pytest.raises(WorkflowAccessError, match="no valid integration admission"):
        require_admission(workflow, "owner", "invented")


def test_declaration_revision_binds_schema_and_every_policy_change(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow)
    revision = workflow_profile(workflow, "owner")["revision"]
    require_admission(workflow, "owner", revision)
    policy(workflow, requiresGui=True)
    assert workflow_profile(workflow, "owner")["revision"] != revision
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner", revision)
    assert error.value.code == "PROFILE_STALE"


def test_json_data_profile_exposes_limits_and_requires_matching_category(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow, capabilities=["json-data"], capabilityClass="json-data")
    profile = workflow_profile(workflow, "owner")
    assert profile["capabilityClass"] == "json-data"
    assert profile["capabilities"] == ["json-data"]
    assert profile["jsonLimits"]["maxBytes"] == 1_048_576
    assert profile["admission"]["allowed"] is True

    policy(workflow, capabilities=["json-data"])
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner")
    assert error.value.code == "CAPABILITY_DECLARATION_INVALID"


def test_service_read_profile_exposes_component_operations_and_transports(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(
        workflow,
        capabilities=["service-http-read"],
        capabilityClass="service-http-read",
        componentOperations=["Network.http_request"],
        allowedTransports=["mcp", "rest"],
        readOnlyReview={
            "version": 1,
            "boundedResources": True,
            "readOnlyConnections": True,
            "operationInputs": {"Network.http_request": {"request_type": "get", "file_path": "", "save_type": "no"}},
        },
    )
    profile = workflow_profile(workflow, "owner")
    assert profile["admission"]["allowed"] is True
    assert profile["componentOperations"] == ["Network.http_request"]
    assert profile["allowedTransports"] == ["mcp", "rest"]


@pytest.mark.parametrize(
    "change",
    [
        {"componentOperations": None},
        {"componentOperations": ["Network.ftp_upload"]},
        {"requiresGui": True},
        {"requiresHuman": True},
        {"sideEffects": ["external-write"]},
    ],
)
def test_service_read_profile_rejects_incomplete_or_writing_shape(policy, change):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    declaration = {
        "capabilities": ["service-http-read"],
        "capabilityClass": "service-http-read",
        "componentOperations": ["Network.http_request"],
        "allowedTransports": ["mcp"],
        "readOnlyReview": {
            "version": 1,
            "boundedResources": True,
            "readOnlyConnections": True,
            "operationInputs": {"Network.http_request": {"request_type": "get", "file_path": "", "save_type": "no"}},
        },
    }
    declaration.update(change)
    policy(workflow, **declaration)
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner")
    assert error.value.code in {"PROFILE_INCOMPLETE", "CAPABILITY_DECLARATION_INVALID"}


@pytest.mark.parametrize(
    "change",
    [
        {"capabilities": ["json-data"], "capabilityClass": "json-data", "fileInputs": True},
        {"capabilities": ["json-data"], "capabilityClass": "json-data", "requiresGui": True},
        {
            "capabilities": ["json-data"],
            "capabilityClass": "json-data",
            "outputSchema": {"type": "object", "properties": {"x": {"$ref": "https://example.invalid"}}},
        },
    ],
)
def test_json_data_profile_rejects_unsupported_declarations(policy, change):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow, **change)
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner")
    assert error.value.code in {"JSON_DATA_UNSUPPORTED", "OUTPUT_SCHEMA_UNSUPPORTED"}


def test_corrupt_policy_does_not_revert_to_legacy(tmp_path, monkeypatch):
    path = tmp_path / "invalid.json"
    path.write_text("{broken")
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", str(path))
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner")
    assert error.value.code == "INTEGRATION_POLICY_UNAVAILABLE"


def test_unchanged_policy_is_read_and_parsed_once(policy, monkeypatch):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow)
    reads = []
    parses = []
    read_text = Path.read_text
    validate_json = Policy.model_validate_json

    def read(path, *args, **kwargs):
        reads.append(path)
        return read_text(path, *args, **kwargs)

    def validate(data):
        parses.append(data)
        return validate_json(data)

    monkeypatch.setattr(Path, "read_text", read)
    monkeypatch.setattr(Policy, "model_validate_json", validate)
    for _ in range(3):
        assert workflow_profile(workflow, "owner")["admission"]["allowed"]
    assert len(reads) == len(parses) == 1


def test_policy_cache_invalidates_on_mtime_change(tmp_path, monkeypatch):
    path = tmp_path / "policy.json"
    path.write_text('{"enforcedUsers":["owner"]}', encoding="utf-8")
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", str(path))
    assert load_policy().enforcedUsers == ["owner"]
    previous = path.stat()
    path.write_text('{"enforcedUsers":["other"]}', encoding="utf-8")
    os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))
    assert load_policy().enforcedUsers == ["other"]


def test_policy_cache_invalidates_on_atomic_replacement(policy):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow)
    path = Path(get_settings().INTEGRATION_POLICY_FILE)
    assert workflow_profile(workflow, "owner")["admission"]["allowed"]
    previous = path.stat()
    replacement = path.with_suffix(".new")
    # Keep both length and mtime unchanged: the file identity must invalidate it.
    replacement.write_text(
        path.read_text(encoding="utf-8").replace('"allowed": true', '"allowed":false'), encoding="utf-8"
    )
    os.utime(replacement, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    replacement.replace(path)
    assert path.stat().st_size == previous.st_size
    assert workflow_profile(workflow, "owner")["admission"]["reason"] == "PROFILE_DENIED"


@pytest.mark.parametrize("failure", ["missing", "malformed", "invalid-schema", "unreadable"])
def test_policy_cache_does_not_reuse_valid_policy_after_failure(policy, monkeypatch, failure):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow)
    path = Path(get_settings().INTEGRATION_POLICY_FILE)
    assert workflow_profile(workflow, "owner")["admission"]["allowed"]
    with monkeypatch.context() as patch:
        if failure == "missing":
            path.unlink()
        elif failure in ("malformed", "invalid-schema"):
            path.write_text("{broken" if failure == "malformed" else '{"enforcedUsers":false}', encoding="utf-8")
        else:
            previous = path.stat()
            os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))

            def denied(*args, **kwargs):
                raise PermissionError("private deployment path")

            patch.setattr(Path, "read_text", denied)
        with pytest.raises(WorkflowAccessError) as error:
            require_admission(workflow, "owner")
        assert error.value.code == "INTEGRATION_POLICY_UNAVAILABLE"
        assert "private deployment path" not in str(error.value)
    policy(workflow, allowed=False)
    assert workflow_profile(workflow, "owner")["admission"]["reason"] == "PROFILE_DENIED"


def test_policy_cache_isolated_by_path_and_from_caller_mutations(tmp_path, monkeypatch):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text('{"enforcedUsers":["owner"]}', encoding="utf-8")
    second.write_text('{"enforcedUsers":["other"]}', encoding="utf-8")
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", str(first))
    load_policy().enforcedUsers.clear()
    assert load_policy().enforcedUsers == ["owner"]
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", str(second))
    assert load_policy().enforcedUsers == ["other"]
    monkeypatch.setattr(get_settings(), "INTEGRATION_POLICY_FILE", "")
    assert load_policy().enforcedUsers == []


def test_policy_update_during_read_is_not_cached(policy, monkeypatch):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow)
    read_text = Path.read_text

    def read_then_replace(path, *args, **kwargs):
        contents = read_text(path, *args, **kwargs)
        policy(workflow, allowed=False)
        return contents

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_text", read_then_replace)
        with pytest.raises(WorkflowAccessError) as error:
            require_admission(workflow, "owner")
        assert error.value.code == "INTEGRATION_POLICY_UNAVAILABLE"
    assert workflow_profile(workflow, "owner")["admission"]["reason"] == "PROFILE_DENIED"


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"allowed": False}, "PROFILE_DENIED"),
        ({"requiresGui": None}, "PROFILE_INCOMPLETE"),
        ({"fileInputs": True}, "FILE_TRANSFER_UNSUPPORTED"),
        ({"inputSchemaHash": "0" * 64}, "PROFILE_STALE"),
        ({"version": 9}, "PROFILE_UNKNOWN"),
    ],
)
def test_scoped_denials_are_fail_closed(policy, change, reason):
    workflow = Workflow(project_id="p", user_id="owner", version=1, parameters="[]")
    policy(workflow, **change)
    with pytest.raises(WorkflowAccessError) as error:
        require_admission(workflow, "owner")
    assert error.value.code == reason


@pytest.mark.asyncio
async def test_json_data_execution_freezes_data_contract_and_rejects_mismatch(database, policy, monkeypatch):
    monkeypatch.setattr(
        "app.services.execution.management.capabilities",
        AsyncMock(return_value={"protocol": 1, "clientId": "client", "supportsCancel": True}),
    )
    with Session(database) as db:
        workflow = db.get(Workflow, "allowed")
        policy(workflow, capabilities=["json-data"], capabilityClass="json-data")
        profile = workflow_profile(workflow, "owner")
        service = ExecutionService(AsyncSessionAdapter(db))
        # Capture the frozen metadata without spawning a background execution task.
        service.execute_workflow = AsyncMock()

        await service.execute_authorized_workflow(
            ExecutionCreate(project_id="allowed", version=2, params={}, capability_class="json-data"),
            "owner",
            wait=False,
        )
        contract = json.loads(service.execute_workflow.await_args.kwargs["metadata"]["data_contract"])
        assert contract == {
            "version": 1,
            "profileRevision": profile["revision"],
            "inputSchemaHash": profile["inputSchemaHash"],
            "outputSchema": None,
            "limits": profile["jsonLimits"],
        }

        # A caller may not claim a class the workflow is not admitted for.
        policy(workflow)
        with pytest.raises(WorkflowAccessError) as error:
            await service.execute_authorized_workflow(
                ExecutionCreate(project_id="allowed", version=2, params={}, capability_class="json-data"),
                "owner",
                wait=False,
            )
        assert error.value.code == "CAPABILITY_NOT_ALLOWED"


@pytest.mark.asyncio
async def test_all_execution_callers_share_admission(database, policy):
    with Session(database) as db:
        workflow = db.get(Workflow, "allowed")
        policy(workflow, allowed=False)
        service = ExecutionService(AsyncSessionAdapter(db))
        service.execute_workflow = AsyncMock()
        for request in [
            ExecutionCreate(project_id="allowed", version=2),
            ExecutionCreate(project_id="allowed", version=2, profile_revision="review-1"),
        ]:
            with pytest.raises(WorkflowAccessError) as error:
                await service.execute_authorized_workflow(request, "owner")
            assert error.value.code == "PROFILE_DENIED"
        service.execute_workflow.assert_not_awaited()
        assert len(db.execute(select(Execution)).scalars().all()) == 1


@pytest.mark.asyncio
async def test_running_execution_survives_republication(database):
    with Session(database) as db:
        db.get(Workflow, "allowed").version = 3
        db.commit()
        result = await WorkflowControlService(AsyncSessionAdapter(db)).get_execution("existing", "owner")
        assert result["executionId"] == "existing"
        assert result["version"] == 2
