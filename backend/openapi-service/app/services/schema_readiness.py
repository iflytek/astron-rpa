"""Reject an unmigrated execution database before accepting any traffic."""

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.models.workflow import Execution, Workflow

MIGRATION_HELP = (
    "Stop OpenAPI and follow EXECUTION_MANAGEMENT.md: apply missing migrations "
    "001_execution_management.sql and 002_json_data_contract.sql in order before restarting."
)


def validate_execution_schema(connection):
    inspector = inspect(connection)
    missing = []
    undersized = []
    incompatible_charsets = []
    for model in (Workflow, Execution):
        table = model.__table__
        if not inspector.has_table(table.name):
            missing.append(table.name)
            continue
        actual = {column["name"]: column for column in inspector.get_columns(table.name)}
        missing.extend(f"{table.name}.{column.name}" for column in table.columns if column.name not in actual)
        if connection.dialect.name in ("mysql", "mariadb"):
            options = inspector.get_table_options(table.name)
            default_charset = options.get(f"{connection.dialect.name}_default charset")
            for name in ("parameters", "result", "data_contract"):
                if name in table.columns and name in actual:
                    # LONGTEXT is also compatible with the bounded JSON contract.
                    if str(actual[name]["type"]).upper() not in ("MEDIUMTEXT", "LONGTEXT"):
                        undersized.append(f"{table.name}.{name}")
                    charset = getattr(actual[name]["type"], "charset", None) or default_charset
                    if charset != "utf8mb4":
                        incompatible_charsets.append(f"{table.name}.{name}")
    if missing or undersized or incompatible_charsets:
        details = []
        if missing:
            details.append("missing tables/columns: " + ", ".join(missing))
        if undersized:
            details.append("columns require MEDIUMTEXT or LONGTEXT: " + ", ".join(undersized))
        if incompatible_charsets:
            details.append("columns require utf8mb4: " + ", ".join(incompatible_charsets))
        raise RuntimeError("OpenAPI execution schema is not ready; " + "; ".join(details) + ". " + MIGRATION_HELP)


async def check_execution_schema():
    try:
        async with engine.connect() as connection:
            await connection.run_sync(validate_execution_schema)
    except SQLAlchemyError:
        # Do not include a connection URL or driver exception in the diagnostic.
        raise RuntimeError(
            "OpenAPI execution schema check failed; verify database connectivity. " + MIGRATION_HELP
        ) from None
