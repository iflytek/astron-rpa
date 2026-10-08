from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.exc import OperationalError

from app import main
from app.models.workflow import Execution, Workflow
from app.services import schema_readiness


@pytest.fixture
def schema_engine():
    engine = create_engine("sqlite://")
    Workflow.__table__.create(engine)
    Execution.__table__.create(engine)
    yield engine
    engine.dispose()


def test_current_execution_schema_is_accepted_without_writes(schema_engine):
    with schema_engine.connect() as connection:
        schema_readiness.validate_execution_schema(connection)
        assert connection.execute(text("SELECT count(*) FROM openai_executions")).scalar_one() == 0


@pytest.mark.parametrize("column", ["data_contract", "client_id"])
def test_old_execution_schema_is_rejected_with_upgrade_instructions(schema_engine, column):
    with schema_engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE openai_executions DROP COLUMN {column}"))
        with pytest.raises(RuntimeError) as error:
            schema_readiness.validate_execution_schema(connection)
        message = str(error.value)
        assert f"openai_executions.{column}" in message
        assert "001_execution_management.sql" in message
        assert "002_json_data_contract.sql" in message


def test_missing_workflow_table_is_rejected(schema_engine):
    with schema_engine.begin() as connection:
        Workflow.__table__.drop(connection)
        with pytest.raises(RuntimeError, match="missing tables/columns: openai_workflows"):
            schema_readiness.validate_execution_schema(connection)


@pytest.mark.asyncio
async def test_schema_failure_aborts_startup_before_runtime_initialization(monkeypatch):
    check = AsyncMock(side_effect=RuntimeError("missing openai_executions.data_contract"))
    redis, websocket, recovery = AsyncMock(), AsyncMock(), AsyncMock()
    monkeypatch.setattr(main, "check_execution_schema", check)
    monkeypatch.setattr(main, "init_redis_pool", redis)
    monkeypatch.setattr(main, "get_ws_service", websocket)
    monkeypatch.setattr(main, "recover_executions", recovery)
    with pytest.raises(RuntimeError, match="data_contract"):
        async with main.lifespan(main.app):
            pytest.fail("An unmigrated service must not become ready")
    check.assert_awaited_once()
    redis.assert_not_awaited()
    websocket.assert_not_awaited()
    recovery.assert_not_awaited()


@pytest.mark.asyncio
async def test_schema_connection_failure_has_safe_diagnostic(monkeypatch):
    engine = MagicMock()
    engine.connect.return_value.__aenter__ = AsyncMock(
        side_effect=OperationalError("private connection", {}, Exception("private password"))
    )
    monkeypatch.setattr(schema_readiness, "engine", engine)
    with pytest.raises(RuntimeError, match="verify database connectivity") as error:
        await schema_readiness.check_execution_schema()
    assert "private" not in str(error.value)


@pytest.mark.parametrize("column_type", ["MEDIUMTEXT", "LONGTEXT", "TEXT"])
def test_mysql_json_capacity_requires_migration(monkeypatch, column_type):
    inspector = MagicMock()
    inspector.has_table.return_value = True
    inspector.get_table_options.return_value = {"mysql_default charset": "utf8mb4"}

    def columns(name):
        model = Workflow if name == Workflow.__tablename__ else Execution
        return [{"name": column.name, "type": column_type} for column in model.__table__.columns]

    inspector.get_columns.side_effect = columns
    monkeypatch.setattr(schema_readiness, "inspect", lambda _: inspector)
    connection = MagicMock()
    connection.dialect.name = "mysql"
    if column_type == "TEXT":
        with pytest.raises(RuntimeError, match="columns require MEDIUMTEXT or LONGTEXT"):
            schema_readiness.validate_execution_schema(connection)
    else:
        schema_readiness.validate_execution_schema(connection)


@pytest.mark.parametrize("dialect", ["mysql", "mariadb"])
@pytest.mark.parametrize(
    ("table_charset", "column_charset", "accepted"),
    [("utf8mb4", None, True), ("utf8mb3", "utf8mb4", True), ("utf8mb3", None, False)],
)
def test_json_columns_require_full_unicode_charset(monkeypatch, dialect, table_charset, column_charset, accepted):
    inspector = MagicMock()
    inspector.has_table.return_value = True
    inspector.get_table_options.return_value = {f"{dialect}_default charset": table_charset}

    def columns(name):
        model = Workflow if name == Workflow.__tablename__ else Execution
        return [{"name": column.name, "type": MEDIUMTEXT(charset=column_charset)} for column in model.__table__.columns]

    inspector.get_columns.side_effect = columns
    monkeypatch.setattr(schema_readiness, "inspect", lambda _: inspector)
    connection = MagicMock()
    connection.dialect.name = dialect
    if accepted:
        schema_readiness.validate_execution_schema(connection)
    else:
        with pytest.raises(RuntimeError, match="columns require utf8mb4"):
            schema_readiness.validate_execution_schema(connection)
