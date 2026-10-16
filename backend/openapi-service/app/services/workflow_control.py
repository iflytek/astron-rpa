"""Authorized workflow control shared by external integrations.

Transport addresses and caller-side polling do not belong in this service.
Execution continues to use the same core as the REST and dynamic MCP APIs.
"""

from datetime import UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Execution, Workflow
from app.schemas.integration import CAPABILITY_CLASSES
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services import execution_management as management
from app.services.execution import ExecutionService
from app.services.integration_policy import workflow_profile
from app.services.workflow import WorkflowService
from app.services.workflow_schema import JSON_LIMITS, validate_arguments, workflow_input_schema

__all__ = ["WorkflowControlError", "WorkflowControlService", "validate_arguments", "workflow_input_schema"]

WorkflowControlError = WorkflowAccessError


class WorkflowControlService:
    def __init__(self, db: AsyncSession):
        self.workflows = WorkflowService(db)
        self.executions = ExecutionService(db)

    async def _authorized_workflow(self, project_id: str, user_id: str, version: int | None = None) -> Workflow:
        return await self.workflows.get_external_workflow(project_id, user_id, version)

    @staticmethod
    def _workflow_summary(workflow: Workflow) -> dict:
        try:
            profile = workflow_profile(workflow, workflow.user_id)
            admission = profile["admission"]
        except WorkflowControlError as exc:
            admission = {"allowed": False, "reason": exc.code, "enforced": None}
            profile = {
                "capabilityClass": None,
                "capabilities": None,
                "componentOperations": None,
                "allowedTransports": None,
            }
        return {
            "projectId": workflow.project_id,
            "name": workflow.name,
            "description": workflow.description or "",
            "version": workflow.version,
            "admission": admission,
            "capabilityClass": profile["capabilityClass"],
            "capabilities": profile["capabilities"],
            "componentOperations": profile["componentOperations"],
            "allowedTransports": profile["allowedTransports"],
        }

    async def list_workflows(self, user_id: str, offset: int = 0, limit: int = 100) -> dict:
        workflows = await self.workflows.get_external_workflows(user_id, skip=offset, limit=limit + 1)
        return {
            "workflows": [self._workflow_summary(workflow) for workflow in workflows[:limit]],
            "nextOffset": offset + limit if len(workflows) > limit else None,
        }

    async def get_workflow(self, project_id: str, user_id: str) -> dict:
        workflow = await self._authorized_workflow(project_id, user_id)
        capability = await management.capabilities(user_id)
        return {
            **self._workflow_summary(workflow),
            "inputSchema": workflow_input_schema(workflow),
            "supportsCancel": bool(capability and capability.get("supportsCancel")),
            "profile": workflow_profile(workflow, user_id),
        }

    async def get_integration(self, user_id: str) -> dict:
        client = {"state": "unsupported", "protocol": None, "supportsCancel": False}
        try:
            capability = await management.capabilities(user_id, required=True)
            if capability:
                client = {"state": "ready", "protocol": 1, "supportsCancel": capability.get("supportsCancel") is True}
        except WorkflowControlError as exc:
            client["state"] = "offline" if exc.code == "CLIENT_OFFLINE" else "unconfirmed"
        return {
            "contractVersion": 1,
            "serviceVersion": "1.0.0+public-framework.1",
            "profileSchemaVersion": 1,
            "requiredClientProtocol": 1,
            "durableIdempotency": True,
            "operations": ["workflow_list", "workflow_get", "workflow_execute", "execution_get", "execution_cancel"],
            "capabilityClasses": list(CAPABILITY_CLASSES),
            "jsonLimits": JSON_LIMITS.copy(),
            "client": client,
            "limitations": ["single-openapi-owner", "controlled-validation", "secret-inputs-suppress-results"],
        }

    async def execute_workflow(
        self,
        project_id: str,
        user_id: str,
        params: dict,
        version: int | None = None,
        idempotency_key: str | None = None,
        execution_timeout: int | None = None,
        profile_revision: str | None = None,
        capability_class: str | None = None,
    ) -> dict:
        # Fixed tools use canonical project IDs; legacy alias resolution stays REST-only.
        # A same-key replay must reach the durable receipt before new-release
        # admission. Still reject the legacy example-project alias here.
        await self._authorized_workflow(project_id, user_id, None if idempotency_key else version)
        execution = await self.executions.execute_authorized_workflow(
            ExecutionCreate(
                project_id=project_id,
                version=version,
                params=params,
                idempotency_key=idempotency_key,
                execution_timeout=execution_timeout,
                profile_revision=profile_revision,
                capability_class=capability_class,
            ),
            user_id,
            wait=False,
            transport="mcp",
        )
        return self.execution_result(execution)

    async def cancel_execution(self, execution_id: str, user_id: str) -> dict:
        return self.execution_result(await self.executions.request_cancellation(execution_id, user_id))

    async def get_execution(self, execution_id: str, user_id: str) -> dict:
        execution = await self.executions.get_authorized_execution(execution_id, user_id)
        if execution is None:
            raise WorkflowControlError("EXECUTION_NOT_FOUND", "Execution not found or access is disabled")
        return self.execution_result(execution)

    @staticmethod
    def execution_result(execution: Execution) -> dict:
        states = {
            "PENDING": "accepted",
            "RUNNING": "running",
            "COMPLETED": "succeeded",
            "FAILED": "failed",
        }
        if execution.protocol == 1:
            states.update(CANCELLED="cancelled", TIMEOUT="timeout")
        state = states.get(execution.status, "unknown")
        result, error = None, None
        reply = execution.get_result_as_dict()
        if state == "succeeded":
            if not isinstance(reply, dict) or reply.get("code") != "0000":
                raise WorkflowControlError("RESULT_UNAVAILABLE", "Stored execution result is unavailable")
            result = reply.get("data")
        elif state == "failed":
            code, message = "EXECUTION_FAILED", "Workflow execution failed"
            if execution.error in management.ERRORS:
                code = execution.error
                message = {
                    "CLIENT_BUSY": "RPA client is busy",
                    "CLIENT_OFFLINE": "RPA client is offline or disconnected",
                    "UNSUPPORTED_RESULT": "Workflow produced an unsupported result",
                    "DISPATCH_EXPIRED": "Execution was not dispatched before the acceptance deadline",
                }.get(code, "Workflow execution failed")
            elif execution.error == "RPA client is offline or disconnected":
                code, message = "CLIENT_OFFLINE", "RPA client is offline or disconnected"
            elif isinstance(reply, dict) and reply.get("msg") in (
                "有任务在运行中",
                "已有实例在运行，无法启动",
                "已有实例运行，启动失败...",
            ):
                code, message = "CLIENT_BUSY", "RPA client is busy"
            error = {"code": code, "message": message}
        elif state == "timeout":
            error = {"code": "EXECUTION_TIMEOUT", "message": "Execution deadline exceeded; process stop confirmed"}
        elif state == "unknown":
            # Neither an observation timeout nor a legacy cancellation record
            # proves the desktop task has stopped.
            code = "EXECUTION_RESULT_TIMEOUT" if execution.status == "UNKNOWN" else "EXECUTION_STATE_UNKNOWN"
            if execution.protocol == 1 and execution.error in management.ERRORS:
                code = execution.error
            error = {"code": code, "message": "Execution outcome is unknown; the client may still be running"}
        terminal = state in ("succeeded", "failed", "cancelled", "timeout")

        def timestamp(value):
            return value.replace(tzinfo=UTC).isoformat() if value else None

        return {
            "executionId": execution.id,
            "projectId": execution.project_id,
            "version": execution.version,
            "status": state,
            "terminal": terminal,
            "acceptedAt": timestamp(execution.start_time),
            "startedAt": timestamp(execution.started_at),
            "finishedAt": timestamp(execution.end_time) if terminal else None,
            "clientId": execution.client_id,
            "runId": execution.run_id,
            "cancelRequested": bool(execution.cancel_requested),
            "result": result,
            "error": error,
            "supportsCancel": bool(execution.protocol == 1 and execution.cancel_supported and not terminal),
            "resultVisibility": "suppressed-for-secret-inputs" if execution.secret_fields else "json",
        }
