"""Stable MCP workflow-control tool definitions."""

from mcp import types


def object_schema(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


PROJECT_ID = {"type": "string", "minLength": 1, "maxLength": 100}
VERSION = {"type": "integer", "minimum": 1}
WORKFLOW_PROPERTIES = {
    "projectId": PROJECT_ID,
    "name": {"type": "string"},
    "description": {"type": "string"},
    "version": VERSION,
    "admission": {"type": "object"},
    "capabilityClass": {"type": ["string", "null"]},
    "capabilities": {"type": ["array", "null"], "items": {"type": "string"}},
}
WORKFLOW_SCHEMA = object_schema(WORKFLOW_PROPERTIES, list(WORKFLOW_PROPERTIES))
EXECUTION_PROPERTIES = {
    "executionId": {"type": "string"},
    "projectId": PROJECT_ID,
    "version": VERSION,
    "status": {"enum": ["accepted", "running", "succeeded", "failed", "cancelled", "timeout", "unknown"]},
    "terminal": {"type": "boolean"},
    "acceptedAt": {"type": ["string", "null"]},
    "finishedAt": {"type": ["string", "null"]},
    "startedAt": {"type": ["string", "null"]},
    "clientId": {"type": ["string", "null"]},
    "runId": {"type": ["string", "null"]},
    "cancelRequested": {"type": "boolean"},
    "result": {},
    "error": {
        "anyOf": [
            {"type": "null"},
            object_schema({"code": {"type": "string"}, "message": {"type": "string"}}, ["code", "message"]),
        ]
    },
    "supportsCancel": {"type": "boolean"},
    "resultVisibility": {"enum": ["json", "suppressed-for-secret-inputs"]},
}
EXECUTION_SCHEMA = object_schema(EXECUTION_PROPERTIES, list(EXECUTION_PROPERTIES))

CONTROL_TOOLS = {
    tool.name: tool
    for tool in (
        types.Tool(
            name="astron_integration_get",
            description="Read integration contract and Client readiness without starting an execution.",
            inputSchema=object_schema({}, []),
            outputSchema={"type": "object"},
            annotations=types.ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        ),
        types.Tool(
            name="astron_workflow_list",
            description="List workflows enabled for the authenticated user. Use projectId for stable references.",
            inputSchema=object_schema(
                {
                    "offset": {"type": "integer", "minimum": 0},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                [],
            ),
            outputSchema=object_schema(
                {"workflows": {"type": "array", "items": WORKFLOW_SCHEMA}, "nextOffset": {"type": ["integer", "null"]}},
                ["workflows", "nextOffset"],
            ),
            annotations=types.ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        ),
        types.Tool(
            name="astron_workflow_get",
            description="Get an authorized workflow's published version and supported JSON input schema.",
            inputSchema=object_schema({"projectId": PROJECT_ID}, ["projectId"]),
            outputSchema=object_schema(
                {
                    **WORKFLOW_PROPERTIES,
                    "inputSchema": {"type": "object"},
                    "supportsCancel": {"type": "boolean"},
                    "profile": {"type": "object"},
                },
                [*WORKFLOW_PROPERTIES, "inputSchema", "supportsCancel", "profile"],
            ),
            annotations=types.ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        ),
        types.Tool(
            name="astron_workflow_execute",
            description=(
                "Start an authorized published workflow asynchronously. Returns executionId before completion. "
                "Use astron_execution_get to observe the result. Reuse idempotencyKey for the same request; "
                "without a key, do not automatically retry. executionTimeout is the RPA process deadline in seconds."
            ),
            inputSchema=object_schema(
                {
                    "projectId": PROJECT_ID,
                    "version": VERSION,
                    "params": {"type": "object"},
                    "idempotencyKey": {"type": "string", "minLength": 1, "maxLength": 200},
                    "executionTimeout": {"type": "integer", "minimum": 1, "maximum": 86400},
                    "capabilityClass": {"enum": ["json-data"]},
                    "profileRevision": {"type": "string", "minLength": 1, "maxLength": 100},
                },
                ["projectId"],
            ),
            outputSchema=EXECUTION_SCHEMA,
            annotations=types.ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
        ),
        types.Tool(
            name="astron_execution_cancel",
            description="Request cancellation of the exact authorized execution. cancelRequested is intent, "
            "not stopped confirmation. Query the same ID for the confirmed terminal outcome.",
            inputSchema=object_schema(
                {"executionId": {"type": "string", "minLength": 1, "maxLength": 36}}, ["executionId"]
            ),
            outputSchema=EXECUTION_SCHEMA,
            annotations=types.ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True),
        ),
        types.Tool(
            name="astron_execution_get",
            description=(
                "Get an accepted execution under current ownership and external-access authorization. "
                "A successful query can report a failed workflow. Unknown does not mean the client stopped."
            ),
            inputSchema=object_schema(
                {"executionId": {"type": "string", "minLength": 1, "maxLength": 36}}, ["executionId"]
            ),
            outputSchema=EXECUTION_SCHEMA,
            annotations=types.ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        ),
    )
}
