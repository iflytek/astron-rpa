import json
import sqlite3
from unittest.mock import Mock

import pytest
from astronverse.database import DatabaseType
from astronverse.database.core_win import DatabaseCore
from astronverse.database.database import Database


def test_connect_query_and_disconnect_return_rows_without_committing_reads():
    connection = DatabaseCore.connect({"sqlite_path": ":memory:"}, DatabaseType.SQLite)
    assert isinstance(connection, sqlite3.Connection)
    try:
        query = getattr(Database.query_sql, "__wrapped__", Database.query_sql)
        assert json.loads(query(connection, "SELECT 42 AS answer, 0 AS zero, NULL AS empty")) == [
            {"answer": 42, "zero": 0, "empty": None}
        ]
        connection.execute("CREATE TABLE sample (value INTEGER)")
        connection.execute("INSERT INTO sample VALUES (1)")
        assert connection.in_transaction
        assert json.loads(query(connection, "SELECT * FROM sample WHERE value=2")) == []
        assert connection.in_transaction
    finally:
        DatabaseCore.disconnect(connection)
    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


@pytest.mark.parametrize("fails", [False, True])
def test_query_always_closes_its_cursor_and_never_commits(fails):
    connection = Mock()
    cursor = connection.cursor.return_value
    cursor.description = [("answer",)]
    cursor.fetchall.return_value = [(42,)]
    if fails:
        cursor.execute.side_effect = ValueError("synthetic query failure")
        with pytest.raises(ValueError):
            DatabaseCore.query(connection, "SELECT 42")
    else:
        assert json.loads(DatabaseCore.query(connection, "SELECT 42")) == [{"answer": 42}]
    cursor.close.assert_called_once()
    connection.commit.assert_not_called()


def test_sqlite_read_only_connection_rejects_writes(tmp_path):
    path = tmp_path / "read.sqlite"
    with sqlite3.connect(path) as writer:
        writer.execute("CREATE TABLE sample (value INTEGER)")
        writer.execute("INSERT INTO sample VALUES (42)")
    connection = DatabaseCore.connect({"sqlite_path": str(path), "read_only": True}, DatabaseType.SQLite)
    try:
        assert json.loads(DatabaseCore.query(connection, "SELECT * FROM sample")) == [{"value": 42}]
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("DELETE FROM sample")
    finally:
        DatabaseCore.disconnect(connection)


def test_database_metadata_is_serializable_and_exposes_read_lifecycle():
    from astronverse.actionlib.atomic import atomicMg

    atomicMg.register(Database)
    metadata = json.loads(atomicMg.json())
    assert {"Database.connect_database", "Database.query_sql", "Database.disconnect_database"} <= set(metadata)
    connect = metadata["Database.connect_database"]
    assert next(p for p in connect["inputList"] if p["key"] == "connect_info")["types"] == "Dict"
