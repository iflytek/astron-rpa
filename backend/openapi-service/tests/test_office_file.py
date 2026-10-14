import hashlib
import json
import time
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.dependencies import get_execution_service, get_user_id_from_api_key
from app.routers.files import router
from app.security.workflow_authorization import WorkflowAccessError
from app.services.integration_files import FILE_LIMITS, IntegrationFileStore, file_name
from app.services.office_file import (
    execution_bundle,
    freeze_authorized_files,
    freeze_files,
    validate_file_result,
    validate_file_review,
)


@pytest.fixture
def files(tmp_path, monkeypatch):
    monkeypatch.setattr(get_settings(), "INTEGRATION_FILE_ROOT", str(tmp_path / "files"))
    monkeypatch.setattr(
        get_settings(), "INTEGRATION_FILE_TRANSFER_URL", "https://rpa.example/api/rpa-openapi/files/transfer"
    )
    return IntegrationFileStore(get_settings().INTEGRATION_FILE_ROOT)


def declaration(**updates):
    values = {
        "fileContract": {
            "version": 1,
            "limits": FILE_LIMITS.copy(),
            "inputs": {"source": [".txt"]},
            "outputs": {"target": "result.txt"},
        },
        "fileReview": {
            "version": 1,
            "workspaceOnly": True,
            "macrosDisabled": True,
            "externalServicesReviewed": True,
            "boundedResources": True,
            "resourcesReleased": True,
            "operations": ["File.file_read", "File.file_write"],
        },
        "componentOperations": ["File.file_read", "File.file_write"],
        "fileInputs": True,
        "fileOutputs": True,
        "allowedTransports": ["mcp"],
        "requiresHuman": False,
        "requiresGui": False,
        "exclusiveTerminal": True,
        "risk": "medium",
        "sideEffects": ["workspace-files"],
    }
    values.update(updates)
    return SimpleNamespace(**values)


SCHEMA = {"type": "object", "properties": {"source": {"type": "string"}, "target": {"type": "string"}}}


def upload(files, owner="owner", content=b"sample", name="sample.txt", key=None):
    row = files.reserve(owner, name, upload_key=key)
    return files.write(row["id"], content)


def test_file_roundtrip_owner_isolation_immutable_retries_and_no_paths(files):
    metadata = upload(files, content="中文\x00file".encode(), key="key")
    assert files.read(metadata["fileId"], "owner")[1] == "中文\x00file".encode()
    assert files.reserve("owner", "sample.txt", upload_key="key")["id"] == metadata["fileId"]
    assert files.write(metadata["fileId"], "中文\x00file".encode()) == metadata
    assert set(metadata) == {"fileId", "fileName", "size", "sha256", "expiresAt"}
    with pytest.raises(WorkflowAccessError) as error:
        files.get(metadata["fileId"], "other")
    assert error.value.code == "FILE_NOT_FOUND"
    with pytest.raises(WorkflowAccessError) as error:
        files.write(metadata["fileId"], b"different")
    assert error.value.code == "FILE_IDEMPOTENCY_CONFLICT"


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "..\\escape",
        "C:\\temp\\a.txt",
        "C:relative",
        "/absolute",
        "NUL",
        "x.txt:ads",
        "x.",
        "x ",
        "bad\x00name",
        "",
        "..",
    ],
)
def test_untrusted_filenames_are_rejected(name):
    with pytest.raises(WorkflowAccessError):
        file_name(name)


def test_size_boundary_empty_file_and_quota(files):
    assert upload(files, content=b"")["size"] == 0
    content = b"x" * FILE_LIMITS["maxFileBytes"]
    assert upload(files, content=content)["size"] == len(content)
    with pytest.raises(WorkflowAccessError) as error:
        upload(files, content=content + b"x")
    assert error.value.code == "FILE_TOO_LARGE"
    for _ in range(8):
        files.reserve("quota-owner", "part.txt")
    files.reserve("quota-owner", "part.txt")
    files.reserve("quota-owner", "part.txt")
    with pytest.raises(WorkflowAccessError) as error:
        files.reserve("quota-owner", "part.txt")
    assert error.value.code == "FILE_QUOTA_EXCEEDED"


def test_expiration_cleanup_and_active_grant_pin(files):
    metadata = upload(files)
    identifier = metadata["fileId"]
    token = files.grant(identifier, "owner", "execution", "read", time.time() + 100)
    assert files.authorize(identifier, token, "read")["execution"] == "execution"
    for mode in ["write"]:
        with pytest.raises(WorkflowAccessError):
            files.authorize(identifier, token, mode)
    with pytest.raises(WorkflowAccessError) as error:
        files.delete(identifier, "owner")
    assert error.value.code == "FILE_IN_USE"
    files.revoke("execution")
    with pytest.raises(WorkflowAccessError):
        files.authorize(identifier, token, "read")
    with files.db() as db:
        db.execute("UPDATE files SET expires=0 WHERE id=?", (identifier,))
    with pytest.raises(WorkflowAccessError) as error:
        files.get(identifier, "owner")
    assert error.value.code == "FILE_EXPIRED"
    files.cleanup()
    assert not files.blob(identifier).exists()


def test_input_output_contract_frozen_and_bound_to_execution(files):
    decl = declaration()
    metadata = upload(files)
    params = {"source": metadata["fileId"], "target": "output:target"}
    validate_file_review(decl, SCHEMA, params)
    frozen = freeze_files(vars(decl), params, "owner", 60)
    record = SimpleNamespace(id=str(uuid4()), user_id="owner", execution_timeout=60)
    bundle = execution_bundle(record, frozen)
    output = files.write(bundle["outputs"]["target"]["fileId"], b"result")
    assert validate_file_result(record, frozen, {"data": {"count": 0}, "files": {"target": output}})
    other = SimpleNamespace(id=str(uuid4()), user_id="owner")
    assert not validate_file_result(other, frozen, {"data": {}, "files": {"target": output}})
    assert not validate_file_result(record, frozen, {"data": {}, "files": {}})
    assert "token" not in json.dumps(frozen)
    assert frozen["inputs"]["source"]["sha256"] == hashlib.sha256(b"sample").hexdigest()


@pytest.mark.parametrize(
    "change",
    [
        {"requiresHuman": True},
        {"exclusiveTerminal": False},
        {"risk": "high"},
        {"componentOperations": ["Process.run_command"]},
        {"fileReview": None},
        {"requiresGui": True},
        {"fileOutputs": False},
        {"allowedTransports": []},
    ],
)
def test_invalid_admission_does_not_enable_file_operations(files, change):
    with pytest.raises(WorkflowAccessError):
        validate_file_review(declaration(**change), SCHEMA)


def test_local_paths_deadline_and_file_extension_are_rejected(files):
    decl = declaration()
    with pytest.raises(WorkflowAccessError):
        validate_file_review(decl, SCHEMA, {"source": "C:\\local.txt", "target": "output:target"})
    metadata = upload(files, name="wrong.exe")
    params = {"source": metadata["fileId"], "target": "output:target"}
    with pytest.raises(WorkflowAccessError) as error:
        freeze_files(vars(decl), params, "owner", None)
    assert error.value.code == "FILE_EXECUTION_DEADLINE_REQUIRED"
    with pytest.raises(WorkflowAccessError) as error:
        freeze_files(vars(decl), params, "owner", 60)
    assert error.value.code == "FILE_TYPE_NOT_ALLOWED"


def test_browser_file_context_and_external_mail_boundaries(files):
    operations = ["BrowserSoftware.get_current_obj", "BrowserElement.create_element", "BrowserElement.screenshot"]
    decl = declaration(componentOperations=operations, requiresGui=True)
    decl.fileReview["operations"] = operations
    validate_file_review(decl, SCHEMA)
    for operation in ["BrowserElement.click", "Email.receive_email"]:
        decl.componentOperations = [operation]
        decl.fileReview["operations"] = [operation]
        decl.requiresGui = operation.startswith("Browser")
        with pytest.raises(WorkflowAccessError):
            validate_file_review(decl, SCHEMA)
    decl.sideEffects.append("external-file-transfer")
    validate_file_review(decl, SCHEMA)


@pytest.mark.asyncio
async def test_rest_upload_download_and_execution_grants(files):
    app = FastAPI()
    app.include_router(router)
    identity = {"owner": "owner"}
    execution = SimpleNamespace(id="execution", user_id="owner", status="RUNNING", secret_fields=None)
    service = SimpleNamespace(
        get_execution_internal=AsyncMock(return_value=execution),
        get_authorized_execution=AsyncMock(return_value=execution),
    )
    app.dependency_overrides[get_user_id_from_api_key] = lambda: identity["owner"]
    app.dependency_overrides[get_execution_service] = lambda: service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://rpa.example") as client:
        reserved = await client.post("/files", json={"fileName": "测试.txt", "uploadKey": "key"})
        assert reserved.status_code == 200
        identifier = reserved.json()["fileId"]
        result = await client.put(f"/files/{identifier}/content", content=b"zero\x00false")
        assert result.status_code == 200
        assert (await client.get(f"/files/{identifier}/content")).content == b"zero\x00false"
        identity["owner"] = "other"
        assert (await client.get(f"/files/{identifier}/content")).status_code == 404
        identity["owner"] = "owner"
        assert (await client.get(f"/files/transfer/{identifier}")).status_code == 403
        token = files.grant(identifier, "owner", "execution", "read", time.time() + 100)
        headers = {"Authorization": "Bearer " + token}
        assert (await client.get(f"/files/transfer/{identifier}", headers=headers)).content == b"zero\x00false"
        assert (
            await client.put(f"/files/transfer/{identifier}", headers=headers, content=b"overwrite")
        ).status_code == 403
        execution.status = "CANCELLED"
        assert (await client.get(f"/files/transfer/{identifier}", headers=headers)).status_code == 403
        files.revoke("execution")
        assert (await client.delete(f"/files/{identifier}")).json() == {"deleted": True}


@pytest.mark.asyncio
async def test_output_access_requires_success_and_current_workflow_authorization(files):
    app = FastAPI()
    app.include_router(router)
    execution = SimpleNamespace(status="FAILED", secret_fields=None)
    service = SimpleNamespace(get_authorized_execution=AsyncMock(return_value=execution))
    app.dependency_overrides[get_user_id_from_api_key] = lambda: "owner"
    app.dependency_overrides[get_execution_service] = lambda: service
    row = files.reserve("owner", "output.txt", execution="execution")
    metadata = files.write(row["id"], b"output")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://rpa.example") as client:
        url = f"/files/{metadata['fileId']}/content"
        assert (await client.get(url)).status_code == 404
        execution.status = "COMPLETED"
        assert (await client.get(url)).content == b"output"
        service.get_authorized_execution.return_value = None
        assert (await client.get(url)).status_code == 404


@pytest.mark.asyncio
async def test_reusing_output_as_input_requires_parent_authorization(files):
    row = files.reserve("owner", "source.txt", execution="parent")
    files.write(row["id"], b"source")
    profile = vars(declaration())
    params = {"source": row["id"], "target": "output:target"}
    service = SimpleNamespace(get_authorized_execution=AsyncMock(return_value=None))
    for parent in [
        None,
        SimpleNamespace(status="FAILED", secret_fields=None),
        SimpleNamespace(status="COMPLETED", secret_fields='["secret"]'),
    ]:
        service.get_authorized_execution.return_value = parent
        with pytest.raises(WorkflowAccessError, match="File request"):
            await freeze_authorized_files(profile, params, "owner", 60, service)
    service.get_authorized_execution.return_value = SimpleNamespace(status="COMPLETED", secret_fields=None)
    assert (await freeze_authorized_files(profile, params, "owner", 60, service))["inputs"]["source"]["fileId"] == row[
        "id"
    ]


@pytest.mark.parametrize(("target", "value"), [("fileContract", True), ("fileReview", True)])
def test_contract_versions_are_integers(files, target, value):
    decl = declaration()
    getattr(decl, target)["version"] = value
    with pytest.raises(WorkflowAccessError):
        validate_file_review(decl, SCHEMA)


def test_duplicate_output_names_and_missing_side_effects_are_rejected(files):
    decl = declaration(sideEffects=[])
    with pytest.raises(WorkflowAccessError):
        validate_file_review(decl, SCHEMA)
    decl = declaration()
    decl.fileContract["outputs"]["second"] = "RESULT.TXT"
    schema = deepcopy(SCHEMA)
    schema["properties"]["second"] = {"type": "string"}
    with pytest.raises(WorkflowAccessError):
        validate_file_review(decl, schema)


def test_cleanup_removes_only_expired_partial_writes_and_unused_output_slots(files):
    import os

    stale = files.root / (str(uuid4()) + ".part")
    recent = files.root / (str(uuid4()) + ".part")
    unrelated = files.root / "unrelated.part"
    for path in [stale, recent, unrelated]:
        path.write_bytes(b"partial")
    os.utime(stale, (0, 0))
    os.utime(unrelated, (0, 0))
    slot = files.reserve("owner", "unused.txt", execution="parent")
    files.revoke("parent")
    files.cleanup()
    assert not stale.exists()
    assert recent.exists()
    assert unrelated.exists()
    with pytest.raises(WorkflowAccessError):
        files.get(slot["id"], ready=False)
