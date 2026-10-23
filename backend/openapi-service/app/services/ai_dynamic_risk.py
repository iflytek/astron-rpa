"""Exact-request admin approval for trusted releases, not an arbitrary-code sandbox."""

import logging
import re
import time

from app.schemas.ai_dynamic_risk import CODE_OPERATIONS, DENIED_OPERATIONS, INFERENCE_OPERATIONS, RISK_OPERATIONS
from app.schemas.desktop_ui import DESKTOP_FILE_OPERATIONS, DESKTOP_OPERATIONS
from app.schemas.integration import SERVICE_READ_OPERATIONS
from app.schemas.office_file import OFFICE_FILE_OPERATIONS
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution_management import digest

logger = logging.getLogger(__name__)
HASH = re.compile(r"[a-f0-9]{64}")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*\.[a-z][a-z0-9_]*")
RISK_CONTRACT = {"version": 1, "approvalMode": "admin-exact-request", "automaticExecution": False}
FILE_REQUIRED_OPERATIONS = OFFICE_FILE_OPERATIONS - frozenset().union(*SERVICE_READ_OPERATIONS.values())


def deny(code="RISK_REVIEW_REQUIRED"):
    raise WorkflowAccessError(code, "A reviewed release and administrator-approved exact request are required")


def hashes(value, *, empty=False):
    return (
        isinstance(value, list)
        and (empty or 1 <= len(value) <= 64)
        and len(value) <= 64
        and all(isinstance(v, str) and HASH.fullmatch(v) for v in value)
        and len(set(value)) == len(value)
    )


def validate_risk_review(declaration):
    operations, review = declaration.componentOperations, declaration.riskReview
    if (
        declaration.riskContract != RISK_CONTRACT
        or type(declaration.riskContract.get("version")) is not int
        or declaration.riskContract.get("automaticExecution") is not False
        or declaration.risk not in {"medium", "high"}
        or declaration.requiresHuman is not False
        or declaration.exclusiveTerminal is not True
        or not declaration.outputSchema
        or not declaration.allowedTransports
        or not operations
        or len(operations) > 256
        or len(set(operations)) != len(operations)
        or any(not NAME.fullmatch(op) for op in operations)
        or set(operations) & DENIED_OPERATIONS
        or any(op.startswith("Dialog.") for op in operations)
        or not set(operations) & RISK_OPERATIONS
        or not isinstance(declaration.sideEffects, list)
        or not set(declaration.sideEffects)
        <= {
            "external-service",
            "external-write",
            "dynamic-code",
            "desktop-interaction",
            "workspace-files",
            "external-file-transfer",
        }
        or (not declaration.fileContract and (declaration.fileInputs or declaration.fileOutputs))
        or declaration.requiresGui != bool(declaration.desktopContract)
        or (set(operations) & DESKTOP_OPERATIONS and not declaration.desktopContract)
        or (set(operations) & DESKTOP_FILE_OPERATIONS and not declaration.fileContract)
        or (set(operations) & FILE_REQUIRED_OPERATIONS and not declaration.fileContract)
        or (
            any(op.startswith(("Excel.", "Docx.", "File.", "Folder.", "Compress.")) for op in operations)
            and not declaration.fileContract
        )
        or (any(op.startswith(("Excel.", "Docx.", "Browser")) for op in operations) and not declaration.desktopContract)
    ):
        deny("RISK_CONTRACT_INVALID")
    if (
        not isinstance(review, dict)
        or set(review)
        != {
            "version",
            "operations",
            "maxOperations",
            "codeHashes",
            "approvals",
            "trustedRelease",
            "sensitiveDataReviewed",
            "destinationsReviewed",
            "resourcesReleased",
        }
        or review["version"] != 1
        or type(review["version"]) is not int
        or any(
            review[k] is not True
            for k in ("trustedRelease", "sensitiveDataReviewed", "destinationsReviewed", "resourcesReleased")
        )
        or type(review["maxOperations"]) is not int
        or not 1 <= review["maxOperations"] <= 10000
        or not isinstance(review["operations"], dict)
        or set(review["operations"]) != set(operations)
        or not hashes(review["codeHashes"], empty=not bool(set(operations) & CODE_OPERATIONS))
        or not isinstance(review["approvals"], list)
        or len(review["approvals"]) > 128
    ):
        deny()
    for operation, rule in review["operations"].items():
        if not isinstance(rule, dict) or set(rule) != {"risk", "argumentHashes"}:
            deny()
        if rule["risk"] not in {"medium", "high"} or (rule["risk"] == "high" and declaration.risk != "high"):
            deny()
        if (
            operation
            in RISK_OPERATIONS
            - INFERENCE_OPERATIONS
            - {"Enterprise.get_shared_variable", "Enterprise.download_from_sharefolder"}
            and rule["risk"] != "high"
        ):
            deny()
        # Only non-agent inference may consume dynamic text. Every other operation,
        # including writes fed by model output, must match reviewed arguments.
        if not hashes(rule["argumentHashes"], empty=operation in INFERENCE_OPERATIONS):
            deny()
    if set(operations) & CODE_OPERATIONS and "dynamic-code" not in declaration.sideEffects:
        deny()
    if declaration.risk == "high" and not set(declaration.sideEffects) & {
        "external-write",
        "dynamic-code",
        "desktop-interaction",
    }:
        deny()
    identities = set()
    for approval in review["approvals"]:
        if (
            not isinstance(approval, dict)
            or set(approval)
            != {"id", "approvedBy", "paramsHash", "keyHash", "executionTimeout", "issuedAt", "expiresAt"}
            or any(
                not isinstance(approval[k], str) or not re.fullmatch(r"[A-Za-z0-9_.@:-]{1,100}", approval[k])
                for k in ("id", "approvedBy")
            )
            or any(
                not isinstance(approval[k], str) or not HASH.fullmatch(approval[k]) for k in ("paramsHash", "keyHash")
            )
            or type(approval["executionTimeout"]) is not int
            or not 1 <= approval["executionTimeout"] <= 3600
            or any(type(approval[k]) is not int for k in ("issuedAt", "expiresAt"))
            or not 0 < approval["expiresAt"] - approval["issuedAt"] <= 86400
            or approval["id"] in identities
            or approval["keyHash"] in identities
        ):
            deny()
        identities.update((approval["id"], approval["keyHash"]))


def freeze_risk(profile, user_id, params, key_hash, timeout):
    from app.services.integration_policy import declaration_revision, load_policy

    if not key_hash or type(timeout) is not int or not 1 <= timeout <= 3600:
        deny("RISK_APPROVAL_REQUIRED")
    declaration = next(
        (
            d
            for d in load_policy().declarations
            if (d.userId, d.projectId, d.version) == (user_id, profile["projectId"], profile["version"])
            and declaration_revision(d) == profile["revision"]
        ),
        None,
    )
    if declaration is None:
        deny("PROFILE_STALE")
    validate_risk_review(declaration)
    now = time.time()
    approval = next(
        (
            a
            for a in declaration.riskReview["approvals"]
            if a["paramsHash"] == digest(params)
            and a["keyHash"] == key_hash
            and a["executionTimeout"] == timeout
            and a["issuedAt"] <= now < a["expiresAt"]
        ),
        None,
    )
    if approval is None:
        # No raw params, keys, provider replies or code enter rejection logs.
        logger.warning("Risk admission denied for project %s version %s", profile["projectId"], profile["version"])
        deny("RISK_APPROVAL_REQUIRED")
    return {
        "version": 1,
        "approval": approval.copy(),
        "profileRevision": profile["revision"],
        "operations": declaration.riskReview["operations"],
        "maxOperations": declaration.riskReview["maxOperations"],
        "codeHashes": declaration.riskReview["codeHashes"],
    }
