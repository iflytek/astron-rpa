from unittest.mock import AsyncMock

import pytest

from app.services.workflow import WorkflowService


@pytest.mark.asyncio
async def test_get_workflows_filters_by_active_status_and_user():
    result = type("ResultStub", (), {})()
    scalars = type("ScalarsStub", (), {})()
    scalars.all = lambda: []
    result.scalars = lambda: scalars
    db = type("DatabaseSessionStub", (), {})()
    db.execute = AsyncMock(return_value=result)
    service = WorkflowService(db)

    assert await service.get_workflows("user-1") == []

    statement = db.execute.await_args.args[0]
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
    assert "workflows.status = 1" in sql
    assert "workflows.user_id = 'user-1'" in sql
