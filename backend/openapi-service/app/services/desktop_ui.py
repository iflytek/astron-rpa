"""Admission for trusted, version-bound desktop workflows, not a Python sandbox."""

from pathlib import PureWindowsPath

from app.schemas.desktop_ui import DESKTOP_FILE_OPERATIONS, DESKTOP_OPERATIONS
from app.schemas.office_file import OFFICE_FILE_OPERATIONS
from app.security.workflow_authorization import WorkflowAccessError


def deny(code="DESKTOP_CONTRACT_INVALID"):
    raise WorkflowAccessError(code, "Desktop workflow requires a valid reviewed execution environment")


def validate_desktop_environment(declaration):
    contract, review = declaration.desktopContract, declaration.desktopReview
    operations = declaration.componentOperations
    if (
        not isinstance(contract, dict)
        or set(contract) != {"version", "resolution", "programs", "humanMode"}
        or type(contract["version"]) is not int
        or contract["version"] != 1
        or not isinstance(contract["resolution"], dict)
        or set(contract["resolution"]) != {"width", "height"}
        or any(type(v) is not int or not 320 <= v <= 16384 for v in contract["resolution"].values())
        or not isinstance(contract["programs"], list)
        or not 1 <= len(contract["programs"]) <= 16
        or any(not isinstance(v, str) or not v or len(v) > 64 for v in contract["programs"])
        or len(set(contract["programs"])) != len(contract["programs"])
        or contract["humanMode"] not in ("none", "attended")
        or declaration.requiresHuman is not (contract["humanMode"] == "attended")
        or declaration.requiresGui is not True
        or declaration.exclusiveTerminal is not True
    ):
        deny()
    if (
        not isinstance(review, dict)
        or set(review)
        != {
            "version",
            "operations",
            "targets",
            "programs",
            "boundedResources",
            "noHighRiskActions",
            "inputBindingsReviewed",
            "resourcesReleased",
        }
        or type(review["version"]) is not int
        or review["version"] != 1
        or review["operations"] != operations
        or any(review[key] is not True for key in ("boundedResources", "inputBindingsReviewed", "resourcesReleased"))
        or not isinstance(review["targets"], list)
        or not 1 <= len(review["targets"]) <= 16
        or any(not isinstance(v, str) or not v.strip() or len(v) > 256 for v in review["targets"])
        or not isinstance(review["programs"], dict)
        or set(review["programs"]) != set(contract["programs"])
    ):
        deny("DESKTOP_REVIEW_REQUIRED")
    for path in review["programs"].values():
        if (
            not isinstance(path, str)
            or len(path) > 1024
            or "\x00" in path
            or not PureWindowsPath(path).is_absolute()
            or path.startswith(("\\\\", "//"))
            or PureWindowsPath(path).suffix.lower() != ".exe"
            or ".." in PureWindowsPath(path).parts
        ):
            deny("DESKTOP_REVIEW_REQUIRED")


def validate_desktop_review(declaration):
    validate_desktop_environment(declaration)
    operations = declaration.componentOperations
    if (
        declaration.risk not in {"low", "medium"}
        or not declaration.allowedTransports
        or not isinstance(declaration.sideEffects, list)
        or "desktop-interaction" not in declaration.sideEffects
        or not set(declaration.sideEffects) <= {"desktop-interaction", "workspace-files", "external-file-transfer"}
        or not operations
        or len(set(operations)) != len(operations)
        or not set(operations) & DESKTOP_OPERATIONS
        or not set(operations) <= DESKTOP_OPERATIONS | (OFFICE_FILE_OPERATIONS if declaration.fileContract else set())
        or (any(op.startswith("Dialog.") for op in operations) and not declaration.requiresHuman)
        or (set(operations) & DESKTOP_FILE_OPERATIONS and not declaration.fileContract)
        or (
            not declaration.fileContract
            and (declaration.fileInputs is not False or declaration.fileOutputs is not False)
        )
        or declaration.desktopReview["noHighRiskActions"] is not True
    ):
        deny()


def freeze_desktop(profile, timeout):
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        deny("DESKTOP_EXECUTION_DEADLINE_REQUIRED")
    # Private targets/program paths travel only on the authenticated client channel.
    # Re-read the same bound declaration; a concurrent policy update fails closed.
    from app.services.integration_policy import declaration_revision, load_policy

    for declaration in load_policy().declarations:
        if (declaration.projectId, declaration.version) != (profile["projectId"], profile["version"]):
            continue
        if declaration_revision(declaration) == profile["revision"]:
            validate_desktop_environment(declaration)
            return {
                **declaration.desktopContract,
                "targets": declaration.desktopReview["targets"],
                "programPaths": declaration.desktopReview["programs"],
            }
    deny("PROFILE_STALE")
