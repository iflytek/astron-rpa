"""Authorized workflow control shared by external integrations.

Transport addresses and caller-side polling do not belong in this service.
Execution continues to use the same core as the REST and dynamic MCP APIs.
"""

import json
import math

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Execution, Workflow
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError
from app.services.execution import ExecutionService
from app.services.workflow import WorkflowService

WorkflowControlError = WorkflowAccessError


def validate_arguments(arguments: dict, schema: dict) -> None:
    try:
        # JSON Schema's number type also accepts non-finite Python floats.
        json.dumps(arguments, allow_nan=False)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(arguments)
    except (ValueError, TypeError, ValidationError, SchemaError):
        # Validator messages include input values; never expose them.
        raise WorkflowControlError("INVALID_ARGUMENTS", "Arguments do not match the tool input schema") from None


def workflow_input_schema(workflow: Workflow) -> dict:
    """Expose scalar parameters without guessing how to serialize runtime objects."""
    try:
        parameters = json.loads(workflow.parameters) if workflow.parameters else []
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        if isinstance(parameters, dict):
            # Existing workflows may already supply a JSON Schema. Limit this
            # entry point to self-contained scalar properties (no remote refs).
            if parameters.get("type") != "object" or set(parameters) - {
                "type",
                "properties",
                "required",
                "additionalProperties",
                "description",
            }:
                raise ValueError
            properties = parameters.get("properties", {})
            if not isinstance(properties, dict):
                raise ValueError
            for prop in properties.values():
                if not isinstance(prop, dict) or prop.get("type") not in ("string", "integer", "number"):
                    raise ValueError
                if set(prop) - {
                    "type",
                    "description",
                    "default",
                    "enum",
                    "minimum",
                    "maximum",
                    "minLength",
                    "maxLength",
                }:
                    raise ValueError
            schema.update(parameters)
            schema["additionalProperties"] = False
        elif isinstance(parameters, list):
            types = {"Str": "string", "Int": "integer", "Float": "number"}
            for param in parameters:
                if not isinstance(param, dict) or param.get("varDirection") not in (0, 1):
                    raise ValueError
                if param["varDirection"] != 0:
                    continue
                name = param.get("varName")
                if not isinstance(name, str) or not name or name in schema["properties"]:
                    raise ValueError
                kind = types[param["varType"]]
                prop = {"type": kind, "description": param.get("varDescribe") or ""}
                default = param.get("varValue")
                if default is None or default == "":
                    schema["required"].append(name)
                else:
                    if kind == "integer":
                        if isinstance(default, bool) or (isinstance(default, float) and not default.is_integer()):
                            raise ValueError
                        default = int(default)
                    elif kind == "number":
                        if isinstance(default, bool):
                            raise ValueError
                        default = float(default)
                        if not math.isfinite(default):
                            raise ValueError
                    prop["default"] = default
                schema["properties"][name] = prop
        else:
            raise ValueError
        Draft202012Validator.check_schema(schema)
        for prop in schema["properties"].values():
            if "default" in prop:
                Draft202012Validator(prop).validate(prop["default"])
        json.dumps(schema, allow_nan=False)
        return schema
    except (KeyError, TypeError, ValueError, SchemaError, ValidationError):
        raise WorkflowControlError(
            "UNSUPPORTED_PARAMETERS", "Workflow inputs require a supported, self-contained scalar schema"
        ) from None


class WorkflowControlService:
    def __init__(self, db: AsyncSession):
        self.workflows = WorkflowService(db)
        self.executions = ExecutionService(db)

    async def _authorized_workflow(self, project_id: str, user_id: str, version: int | None = None) -> Workflow:
        return await self.workflows.get_external_workflow(project_id, user_id, version)

    @staticmethod
    def _workflow_summary(workflow: Workflow) -> dict:
        return {
            "projectId": workflow.project_id,
            "name": workflow.name,
            "description": workflow.description or "",
            "version": workflow.version,
        }

    async def list_workflows(self, user_id: str, offset: int = 0, limit: int = 100) -> dict:
        workflows = await self.workflows.get_external_workflows(user_id, skip=offset, limit=limit + 1)
        return {
            "workflows": [self._workflow_summary(workflow) for workflow in workflows[:limit]],
            "nextOffset": offset + limit if len(workflows) > limit else None,
        }

    async def get_workflow(self, project_id: str, user_id: str) -> dict:
        workflow = await self._authorized_workflow(project_id, user_id)
        return {
            **self._workflow_summary(workflow),
            "inputSchema": workflow_input_schema(workflow),
            "supportsCancel": False,
        }

    async def execute_workflow(self, project_id: str, user_id: str, params: dict, version: int | None = None) -> dict:
        workflow = await self._authorized_workflow(project_id, user_id, version)
        validate_arguments(params, workflow_input_schema(workflow))
        execution = await self.executions.execute_authorized_workflow(
            ExecutionCreate(project_id=workflow.project_id, version=workflow.version, params=params),
            user_id,
            wait=False,
        )
        return self.execution_result(execution)

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
        state = states.get(execution.status, "unknown")
        result, error = None, None
        reply = execution.get_result_as_dict()
        if state == "succeeded":
            if not isinstance(reply, dict) or reply.get("code") != "0000":
                raise WorkflowControlError("RESULT_UNAVAILABLE", "Stored execution result is unavailable")
            result = reply.get("data")
        elif state == "failed":
            code, message = "EXECUTION_FAILED", "Workflow execution failed"
            if execution.error == "RPA client is offline or disconnected":
                code, message = "CLIENT_OFFLINE", "RPA client is offline or disconnected"
            elif isinstance(reply, dict) and reply.get("msg") in (
                "有任务在运行中",
                "已有实例在运行，无法启动",
                "已有实例运行，启动失败...",
            ):
                code, message = "CLIENT_BUSY", "RPA client is busy"
            error = {"code": code, "message": message}
        elif state == "unknown":
            # Neither an observation timeout nor a legacy cancellation record
            # proves the desktop task has stopped.
            code = "EXECUTION_RESULT_TIMEOUT" if execution.status == "UNKNOWN" else "EXECUTION_STATE_UNKNOWN"
            error = {"code": code, "message": "Execution outcome is unknown; the client may still be running"}
        return {
            "executionId": execution.id,
            "projectId": execution.project_id,
            "version": execution.version,
            "status": state,
            "terminal": state in ("succeeded", "failed"),
            "acceptedAt": execution.start_time.isoformat() if execution.start_time else None,
            "finishedAt": execution.end_time.isoformat()
            if execution.end_time and state in ("succeeded", "failed")
            else None,
            "result": result,
            "error": error,
            "supportsCancel": False,
        }
