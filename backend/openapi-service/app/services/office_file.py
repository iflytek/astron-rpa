"""File-workflow admission and immutable execution bindings.

This reviews trusted published workflows. It is not a Python/Office sandbox:
administrators must ensure every local path is derived from the supplied
workspace, macros are disabled and external destinations are approved.
"""

import re
import time
from urllib.parse import urlsplit

from app.config import get_settings
from app.schemas.office_file import OFFICE_FILE_OPERATIONS
from app.services.integration_files import FILE_LIMITS, deny, file_id, file_name, store


def transfer_url():
    value = get_settings().INTEGRATION_FILE_TRANSFER_URL.rstrip("/")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not parsed.path.endswith("/files/transfer")
        or not get_settings().INTEGRATION_FILE_ROOT
    ):
        deny("FILE_TRANSFER_UNAVAILABLE")
    return value


def validate_file_contract(declaration, schema, params=None):
    contract, review = declaration.fileContract, declaration.fileReview
    if (
        not isinstance(contract, dict)
        or set(contract) != {"version", "limits", "inputs", "outputs"}
        or type(contract["version"]) is not int
        or contract["version"] != 1
        or contract["limits"] != FILE_LIMITS
        or not isinstance(contract["inputs"], dict)
        or not isinstance(contract["outputs"], dict)
        or not 1 <= len(contract["inputs"]) + len(contract["outputs"]) <= FILE_LIMITS["maxFiles"]
        or set(contract["inputs"]) & set(contract["outputs"])
        or declaration.fileInputs != bool(contract["inputs"])
        or declaration.fileOutputs != bool(contract["outputs"])
        or not declaration.allowedTransports
        or declaration.exclusiveTerminal is not True
        or not isinstance(declaration.sideEffects, list)
        or (contract["outputs"] and "workspace-files" not in declaration.sideEffects)
        or not declaration.componentOperations
    ):
        deny("FILE_CONTRACT_INVALID")
    external = any(
        op.startswith(("Network.", "Enterprise.", "OpenApi.", "Email."))
        or op in {"BrowserSoftware.upload_web_file", "BrowserSoftware.download_web_file"}
        for op in declaration.componentOperations
    )
    if external and "external-file-transfer" not in declaration.sideEffects:
        deny("FILE_CONTRACT_INVALID")
    if (
        not isinstance(review, dict)
        or type(review.get("version")) is not int
        or review.get("version") != 1
        or any(
            review.get(key) is not True
            for key in (
                "workspaceOnly",
                "macrosDisabled",
                "externalServicesReviewed",
                "boundedResources",
                "resourcesReleased",
            )
        )
        or review.get("operations") != declaration.componentOperations
    ):
        deny("FILE_REVIEW_REQUIRED")
    for key in {*contract["inputs"], *contract["outputs"]}:
        if (
            not isinstance(key, str)
            or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
            or schema.get("properties", {}).get(key, {}).get("type") != "string"
        ):
            deny("FILE_CONTRACT_INVALID")
    for key, extensions in contract["inputs"].items():
        if (
            not isinstance(extensions, list)
            or not extensions
            or not all(isinstance(ext, str) and re.fullmatch(r"\.[a-zA-Z0-9]{1,11}", ext) for ext in extensions)
        ):
            deny("FILE_CONTRACT_INVALID")
        if params is not None:
            file_id(params.get(key))
    for key, name in contract["outputs"].items():
        file_name(name)
        if params is not None and params.get(key) != "output:" + key:
            deny("FILE_OUTPUT_BINDING_INVALID")
    if len({name.casefold() for name in contract["outputs"].values()}) != len(contract["outputs"]):
        deny("FILE_CONTRACT_INVALID")
    transfer_url()


def validate_file_review(declaration, schema, params=None, *, desktop=False):
    from app.schemas.desktop_ui import DESKTOP_OPERATIONS

    allowed_operations = OFFICE_FILE_OPERATIONS | (DESKTOP_OPERATIONS if desktop else set())
    validate_file_contract(declaration, schema, params)
    if (
        (not desktop and declaration.requiresHuman is not False)
        or declaration.risk not in {"low", "medium"}
        or not set(declaration.sideEffects)
        <= ({"workspace-files", "external-file-transfer"} | ({"desktop-interaction"} if desktop else set()))
        or not set(declaration.componentOperations) <= allowed_operations
        or declaration.requiresGui
        is not (desktop or any(op.startswith(("Excel.", "Docx.", "Browser")) for op in declaration.componentOperations))
    ):
        deny("FILE_CONTRACT_INVALID")


async def authorize_file(row, owner, service):
    if row["execution"]:
        execution = await service.get_authorized_execution(row["execution"], owner)
        if execution is None or execution.status != "COMPLETED" or execution.secret_fields:
            deny("FILE_NOT_FOUND")
    return row


async def freeze_authorized_files(profile, params, owner, timeout, service):
    files = store()
    for key in profile["fileContract"]["inputs"]:
        await authorize_file(files.get(params[key], owner), owner, service)
    return freeze_files(profile, params, owner, timeout)


def freeze_files(profile, params, owner, timeout):
    if timeout is None or not 1 <= timeout <= 3600:
        deny("FILE_EXECUTION_DEADLINE_REQUIRED")
    files = store()
    contract = profile["fileContract"]
    inputs = {}
    for key, extensions in contract["inputs"].items():
        row = files.get(params[key], owner)
        if not any(row["name"].lower().endswith(ext.lower()) for ext in extensions):
            deny("FILE_TYPE_NOT_ALLOWED")
        inputs[key] = files.public(row)
    office = [
        name
        for prefix, name in (("Excel.", "excel"), ("Docx.", "word"))
        if any(op.startswith(prefix) for op in profile["componentOperations"])
    ]
    return {"version": 1, "inputs": inputs, "outputs": contract["outputs"], "limits": FILE_LIMITS, "office": office}


def execution_bundle(record, binding):
    files = store()
    base = transfer_url()
    expires = time.time() + min(record.execution_timeout or 3600, 3600) + 600
    inputs, outputs = {}, {}
    for key, metadata in binding["inputs"].items():
        row = files.get(metadata["fileId"], record.user_id)
        if row["sha256"] != metadata["sha256"] or row["size"] != metadata["size"]:
            deny("FILE_INTEGRITY_FAILED")
        inputs[key] = {
            **metadata,
            "url": base + "/" + row["id"],
            "token": files.grant(row["id"], record.user_id, record.id, "read", expires),
        }
    for key, name in binding["outputs"].items():
        row = files.reserve(record.user_id, name, execution=record.id, upload_key="output:" + record.id + ":" + key)
        outputs[key] = {
            "fileId": row["id"],
            "fileName": name,
            "url": base + "/" + row["id"],
            "token": files.grant(row["id"], record.user_id, record.id, "write", expires),
        }
    return {"version": 1, "limits": FILE_LIMITS, "inputs": inputs, "outputs": outputs, "office": binding["office"]}


def validate_file_result(record, binding, value):
    if not isinstance(value, dict) or set(value) != {"data", "files"}:
        return False
    if not isinstance(value["files"], dict) or set(value["files"]) != set(binding["outputs"]):
        return False
    files = store()
    for key, metadata in value["files"].items():
        if not isinstance(metadata, dict):
            return False
        row = files.get(metadata.get("fileId"), record.user_id)
        if row["execution"] != record.id or row["name"] != binding["outputs"][key] or metadata != files.public(row):
            return False
    return True
