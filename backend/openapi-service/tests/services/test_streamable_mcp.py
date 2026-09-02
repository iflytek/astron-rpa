from unittest.mock import AsyncMock

import pytest

from app.services.streamable_mcp import ToolsConfig


@pytest.mark.asyncio
async def test_published_workflow_is_exposed_as_mcp_tool(monkeypatch):
    tools_config = ToolsConfig()

    async def get_published_workflows(user_id: str):
        assert user_id == "user-1"
        return [
            {
                "project_id": "robot-1",
                "name": "Invoice Bot",
                "english_name": "invoice_bot",
                "description": "Process invoices",
                "version": 3,
                "status": 1,
                "parameters": [],
            }
        ]

    monkeypatch.setattr(tools_config, "get_user_workflows", get_published_workflows)

    tools = await tools_config.get_tools_for_user("user-1")

    assert len(tools) == 1
    assert tools[0].name == "invoice_bot"
    assert tools[0].description == "Process invoices"
    assert tools[0].inputSchema == {"type": "object"}


@pytest.mark.asyncio
async def test_workflow_lookup_uses_authenticated_user(monkeypatch):
    tools_config = ToolsConfig()
    workflow = type(
        "WorkflowStub",
        (),
        {"to_dict": lambda self: {"project_id": "robot-1", "status": 1}},
    )()
    workflow_service = type("WorkflowServiceStub", (), {})()
    workflow_service.get_workflows = AsyncMock(return_value=[workflow])
    db = type("DatabaseSessionStub", (), {})()
    db.close = AsyncMock()

    async def get_workflow_service():
        return workflow_service, db

    monkeypatch.setattr(tools_config, "_get_workflow_service", get_workflow_service)

    workflows = await tools_config.get_user_workflows("authenticated-user")

    workflow_service.get_workflows.assert_awaited_once_with("authenticated-user")
    db.close.assert_awaited_once()
    assert workflows == [{"project_id": "robot-1", "status": 1}]
