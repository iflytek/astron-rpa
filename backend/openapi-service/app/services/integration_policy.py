"""Version-bound declarations and admission shared by every execution transport.

No capability is inferred from component names. Administrators enroll users in
the policy explicitly; unclassified releases in that scope fail closed. Other
users retain legacy entry points, but cannot claim framework admission.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import get_settings
from app.models.workflow import Workflow
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution_management import digest
from app.services.workflow_schema import (
    JSON_LIMITS,
    data_output_schema,
    workflow_input_schema,
    workflow_secret_fields,
)

JSON_DATA_CAPABILITY = "json-data"
JSON_DATA_CLASS = "json-data"


class Declaration(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    userId: str = Field(min_length=1)
    projectId: str = Field(min_length=1)
    version: int = Field(ge=1)
    revision: str = Field(min_length=1, max_length=100)
    inputSchemaHash: str = Field(pattern=r"^[a-f0-9]{64}$")
    outputSchema: dict | None = None
    capabilities: list[str] = Field(min_length=1)
    capabilityClass: Literal["json-data"] | None = None
    fileInputs: bool | None = None
    fileOutputs: bool | None = None
    requiresGui: bool | None = None
    requiresHuman: bool | None = None
    environment: list[str] | None = None
    sideEffects: list[str] | None = None
    risk: Literal["low", "medium", "high", "unknown"] = "unknown"
    executionType: Literal["short", "long", "unknown"] = "unknown"
    exclusiveTerminal: bool | None = None
    # This release makes no production capability-layer support claim.
    supportScope: Literal["controlled-validation"] = "controlled-validation"
    allowed: bool = False


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schemaVersion: Literal[1] = 1
    enforcedUsers: list[str] = Field(default_factory=list)
    declarations: list[Declaration] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_scoped_releases(self):
        keys = [(d.userId, d.projectId, d.version) for d in self.declarations]
        if len(keys) != len(set(keys)) or any(d.userId not in self.enforcedUsers for d in self.declarations):
            raise ValueError("Declarations must be unique and belong to the enforced scope")
        return self


def load_policy() -> Policy:
    path = get_settings().INTEGRATION_POLICY_FILE
    if not path:
        return Policy()
    try:
        return Policy.model_validate_json(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # Never silently revert to legacy admission on a broken deployment file.
        raise WorkflowAccessError("INTEGRATION_POLICY_UNAVAILABLE", "Integration policy is unavailable") from None


def workflow_profile(workflow: Workflow, user_id: str) -> dict:
    policy = load_policy()
    schema = workflow_input_schema(workflow)
    declaration = next(
        (
            d
            for d in policy.declarations
            if (d.userId, d.projectId, d.version) == (user_id, workflow.project_id, workflow.version)
        ),
        None,
    )
    reason = "PROFILE_UNKNOWN"
    public = {
        "revision": None,
        "revisionLabel": None,
        "outputSchema": None,
        "capabilities": None,
        "capabilityClass": None,
        "fileInputs": None,
        "fileOutputs": None,
        "requiresGui": None,
        "requiresHuman": None,
        "environment": None,
        "sideEffects": None,
        "risk": "unknown",
        "executionType": "unknown",
        "exclusiveTerminal": None,
        "supportScope": None,
        "jsonLimits": None,
    }
    if declaration:
        public.update(declaration.model_dump(exclude={"userId", "projectId", "version", "allowed", "inputSchemaHash"}))
        output_schema_invalid = False
        if declaration.capabilityClass == JSON_DATA_CLASS and declaration.outputSchema is not None:
            try:
                public["outputSchema"] = data_output_schema(declaration.outputSchema)
            except WorkflowAccessError:
                output_schema_invalid = True
                public["outputSchema"] = None
        public["revisionLabel"] = declaration.revision
        # Bind every declaration change, even if an administrator forgets to
        # increment its human-readable label.
        revision_data = declaration.model_dump()
        if declaration.capabilityClass is None:
            # Preserve existing framework revisions when this optional field is absent.
            revision_data.pop("capabilityClass")
        else:
            revision_data["jsonLimits"] = JSON_LIMITS
            revision_data["dataContractVersion"] = 1
        public["revision"] = digest(revision_data)
        unknown = (
            any(
                public[k] is None
                for k in (
                    "fileInputs",
                    "fileOutputs",
                    "requiresGui",
                    "requiresHuman",
                    "environment",
                    "sideEffects",
                    "exclusiveTerminal",
                )
            )
            or declaration.risk == "unknown"
            or declaration.executionType == "unknown"
        )
        category_invalid = (JSON_DATA_CAPABILITY in declaration.capabilities) != (
            declaration.capabilityClass == JSON_DATA_CLASS
        )
        category_unsupported = declaration.capabilityClass == JSON_DATA_CLASS and (
            declaration.fileInputs or declaration.fileOutputs or declaration.requiresGui
        )
        if output_schema_invalid:
            reason = "OUTPUT_SCHEMA_UNSUPPORTED"
        elif declaration.inputSchemaHash != digest(schema):
            reason = "PROFILE_STALE"
        elif unknown:
            reason = "PROFILE_INCOMPLETE"
        elif category_invalid:
            reason = "CAPABILITY_DECLARATION_INVALID"
        elif category_unsupported:
            reason = "JSON_DATA_UNSUPPORTED"
        elif not declaration.allowed:
            reason = "PROFILE_DENIED"
        elif declaration.fileInputs or declaration.fileOutputs:
            reason = "FILE_TRANSFER_UNSUPPORTED"
        else:
            reason = None
        if declaration.capabilityClass == JSON_DATA_CLASS:
            public["jsonLimits"] = JSON_LIMITS.copy()
    return {
        "schemaVersion": 1,
        "projectId": workflow.project_id,
        "version": workflow.version,
        "inputSchemaHash": digest(schema),
        **public,
        "admission": {"allowed": reason is None, "reason": reason, "enforced": user_id in policy.enforcedUsers},
        "resultVisibility": "suppressed-for-secret-inputs" if workflow_secret_fields(workflow, schema) else "json",
    }


def require_admission(workflow: Workflow, user_id: str, revision: str | None = None) -> dict:
    profile = workflow_profile(workflow, user_id)
    if profile["admission"]["enforced"] or revision is not None:
        if not profile["admission"]["allowed"]:
            raise WorkflowAccessError(
                profile["admission"]["reason"], "Published workflow has no valid integration admission"
            )
        if revision is not None and revision != profile["revision"]:
            raise WorkflowAccessError("PROFILE_STALE", "The workflow declaration changed; prepare a new request")

    return profile
