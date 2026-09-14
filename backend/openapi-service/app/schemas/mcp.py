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
}
WORKFLOW_SCHEMA = object_schema(WORKFLOW_PROPERTIES, list(WORKFLOW_PROPERTIES))
EXECUTION_PROPERTIES = {
    "executionId": {"type": "string"},
    "projectId": PROJECT_ID,
    "version": VERSION,
    "status": {"enum": ["accepted", "running", "succeeded", "failed", "unknown"]},
    "terminal": {"type": "boolean"},
    "acceptedAt": {"type": ["string", "null"]},
    "finishedAt": {"type": ["string", "null"]},
    "result": {},
    "error": {
        "anyOf": [
            {"type": "null"},
            object_schema({"code": {"type": "string"}, "message": {"type": "string"}}, ["code", "message"]),
        ]
    },
    "supportsCancel": {"const": False},
}
EXECUTION_SCHEMA = object_schema(EXECUTION_PROPERTIES, list(EXECUTION_PROPERTIES))

CONTROL_TOOLS = {
    tool.name: tool
    for tool in (
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
            description="Get an authorized workflow's published version and supported scalar input schema.",
            inputSchema=object_schema({"projectId": PROJECT_ID}, ["projectId"]),
            outputSchema=object_schema(
                {**WORKFLOW_PROPERTIES, "inputSchema": {"type": "object"}, "supportsCancel": {"const": False}},
                [*WORKFLOW_PROPERTIES, "inputSchema", "supportsCancel"],
            ),
            annotations=types.ToolAnnotations(readOnlyHint=True, openWorldHint=False),
        ),
        types.Tool(
            name="astron_workflow_execute",
            description=(
                "Start an authorized published workflow asynchronously. Returns executionId before completion. "
                "Use astron_execution_get to observe the result. Non-idempotent: do not automatically retry."
            ),
            inputSchema=object_schema(
                {"projectId": PROJECT_ID, "version": VERSION, "params": {"type": "object"}}, ["projectId"]
            ),
            outputSchema=EXECUTION_SCHEMA,
            annotations=types.ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
        ),
        types.Tool(
            name="astron_execution_get",
            description=(
                "Get an execution's status and result under the current user's workflow/version authorization. "
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
