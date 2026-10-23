"""Authenticated binary transfer; external callers never submit filesystem paths."""

import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.dependencies import get_execution_service, get_user_id_from_api_key
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution import ExecutionService
from app.services.integration_files import FILE_LIMITS, store
from app.services.office_file import authorize_file

router = APIRouter(prefix="/files", tags=["files"])
Owner = Annotated[str, Depends(get_user_id_from_api_key)]
Service = Annotated[ExecutionService, Depends(get_execution_service)]


class FileUpload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    fileName: str = Field(min_length=1, max_length=160)
    uploadKey: str = Field(min_length=1, max_length=200)


def failure(error):
    status = 413 if error.code in {"FILE_TOO_LARGE", "FILE_QUOTA_EXCEEDED"} else 400
    if error.code in {"FILE_NOT_FOUND", "FILE_EXPIRED"}:
        status = 404
    if error.code == "FILE_PERMISSION_DENIED":
        status = 403
    raise HTTPException(status, detail={"code": error.code}) from None


async def bounded_body(request):
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > FILE_LIMITS["maxFileBytes"]:
            raise WorkflowAccessError("FILE_TOO_LARGE", "File exceeds the transfer limit")
        data.extend(chunk)
    return bytes(data)


def binary(row, content):
    return Response(
        content,
        media_type="application/octet-stream",
        headers={"Cache-Control": "no-store", "X-Content-SHA256": row["sha256"], "X-Content-Type-Options": "nosniff"},
    )


async def check_owner_file(files, identifier, owner, service, *, ready=True):
    row = files.get(identifier, owner, ready=ready)
    return await authorize_file(row, owner, service)


@router.post("")
async def create_file(body: FileUpload, user_id: Owner):
    try:
        files = store()
        key = "input:" + hashlib.sha256(body.uploadKey.encode()).hexdigest()
        return files.public(files.reserve(user_id, body.fileName, upload_key=key))
    except WorkflowAccessError as error:
        failure(error)


@router.put("/{identifier}/content")
async def upload_file(identifier: str, request: Request, user_id: Owner):
    try:
        files = store()
        row = files.get(identifier, user_id, ready=False)
        if row["execution"]:
            raise WorkflowAccessError("FILE_PERMISSION_DENIED", "Execution outputs are immutable")
        return files.write(identifier, await bounded_body(request))
    except WorkflowAccessError as error:
        failure(error)


@router.get("/{identifier}")
async def file_metadata(
    identifier: str,
    user_id: Owner,
    service: Service,
):
    try:
        files = store()
        return files.public(await check_owner_file(files, identifier, user_id, service))
    except WorkflowAccessError as error:
        failure(error)


@router.get("/{identifier}/content")
async def download_file(
    identifier: str,
    user_id: Owner,
    service: Service,
):
    try:
        files = store()
        await check_owner_file(files, identifier, user_id, service)
        return binary(*files.read(identifier, user_id))
    except WorkflowAccessError as error:
        failure(error)


@router.delete("/{identifier}")
async def delete_file(identifier: str, user_id: Owner):
    try:
        store().delete(identifier, user_id)
        return {"deleted": True}
    except WorkflowAccessError as error:
        failure(error)


@router.api_route("/transfer/{identifier}", methods=["GET", "PUT"])
async def client_transfer(identifier: str, request: Request, service: Service):
    try:
        files = store()
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise WorkflowAccessError("FILE_PERMISSION_DENIED", "Transfer grant required")
        mode = "read" if request.method == "GET" else "write"
        grant = files.authorize(identifier, authorization[7:], mode)
        execution = await service.get_execution_internal(grant["execution"])
        if execution is None or execution.status not in {"PENDING", "RUNNING", "UNKNOWN"}:
            raise WorkflowAccessError("FILE_PERMISSION_DENIED", "Execution is not active")
        if mode == "read":
            return binary(*files.read(identifier, execution.user_id))
        row = files.get(identifier, execution.user_id, ready=False)
        if row["execution"] != execution.id:
            raise WorkflowAccessError("FILE_PERMISSION_DENIED", "Execution does not own this output")
        return files.write(identifier, await bounded_body(request))
    except WorkflowAccessError as error:
        failure(error)
