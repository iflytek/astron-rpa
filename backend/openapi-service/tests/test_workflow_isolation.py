import os
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/test")
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.routers.workflows import get_workflow as get_workflow_route
from app.services.workflow import WorkflowService


def empty_scalar_result():
    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    return result


@pytest.mark.asyncio
async def test_external_workflow_lookup_filters_by_project_and_user_id():
    db = AsyncMock()
    db.execute.return_value = empty_scalar_result()
    service = WorkflowService(db)

    workflow = await service.get_workflow("project-owned-by-a", "user-b")

    assert workflow is None
    statements = [call.args[0] for call in db.execute.await_args_list]
    assert statements
    for statement in statements:
        compiled = statement.compile()
        assert "user-b" in compiled.params.values()
        assert "user_id" in str(statement.whereclause)


@pytest.mark.asyncio
async def test_workflow_detail_route_uses_authenticated_user_filter():
    service = AsyncMock()
    service.get_workflow.return_value = None

    response = await get_workflow_route(
        project_id="project-owned-by-a",
        user_id="user-b",
        service=service,
    )

    service.get_workflow.assert_awaited_once_with("project-owned-by-a", "user-b")
    assert response.data is None
