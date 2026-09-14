"""Resource policy shared by fixed/dynamic MCP and external REST calls."""

from app.models.workflow import Execution, Workflow


class WorkflowAccessError(Exception):
    """Safe denial; protocol adapters choose their response envelope."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def require_workflow_access(workflow: Workflow | None, user_id: str, version: int | None = None) -> Workflow:
    if (
        workflow is None
        or workflow.user_id != user_id
        or workflow.status != 1
        or not isinstance(workflow.version, int)
        or workflow.version < 1
    ):
        raise WorkflowAccessError("WORKFLOW_NOT_FOUND", "Workflow not found or external access is disabled")
    if version is not None and version != workflow.version:
        raise WorkflowAccessError("VERSION_NOT_ALLOWED", "Requested version is not enabled for external access")
    return workflow


def external_execution_dict(execution: Execution) -> dict:
    """Preserve the REST envelope without exposing stored internal exceptions."""
    result = execution.to_dict()
    if result.get("error") and result["error"] not in (
        "RPA client is offline or disconnected",
        "Execution result timed out; the client may still be running",
    ):
        result["error"] = "Workflow execution failed"
    return result
