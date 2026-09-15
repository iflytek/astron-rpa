import json

import pytest

from app.models.workflow import Workflow
from app.security.workflow_authorization import WorkflowAccessError
from app.services.workflow_schema import bind_arguments, secret_fields, workflow_input_schema


def schema(parameters):
    return workflow_input_schema(Workflow(parameters=json.dumps(parameters)))


def test_published_metadata_native_json_defaults_enum_dates_and_secret():
    parameters = [
        {"varName": "count", "varType": "Int", "varValue": 0},
        {"varName": "ratio", "varType": "Float", "varValue": 0.0},
        {"varName": "enabled", "varType": "Bool", "varValue": False},
        {"varName": "items", "varType": "List", "varValue": [0, False, None]},
        {"varName": "object", "varType": "Dict", "varValue": {"nested": []}},
        {"varName": "choice", "varType": "Str", "enum": ["a", "b"], "varValue": "a"},
        {"varName": "date", "varType": "Date", "varValue": "2026-09-01"},
        {"varName": "instant", "varType": "DateTime", "varValue": "2026-09-01T00:00:00+08:00"},
        {"varName": "empty", "varType": "Str", "nullable": True, "varValue": None},
        {"varName": "secret", "varType": "Password", "varValue": "private-default"},
    ]
    contract = schema([{**item, "varDirection": 0} for item in parameters])
    assert "private-default" not in json.dumps(contract)
    assert contract["required"] == ["secret"]
    assert secret_fields(contract) == ["secret"]
    values = bind_arguments({"secret": "runtime-value"}, contract)
    assert values["count"] == 0
    assert type(values["count"]) is int
    assert values["enabled"] is False
    assert values["empty"] is None
    assert values["items"] == [0, False, None]
    for key, value in [
        ("count", True),
        ("enabled", "false"),
        ("ratio", float("nan")),
        ("choice", "c"),
        ("date", "2026-02-30"),
        ("instant", "2026-09-01T00:00:00"),
        ("instant", "2026-09-01T00:00:00+00:60"),
    ]:
        with pytest.raises(WorkflowAccessError):
            bind_arguments({**values, key: value}, contract)


def test_nested_schema_defaults_and_invalid_file_or_reference_rejected():
    contract = schema(
        {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "default": 0},
                            "secret": {"type": "string", "writeOnly": True},
                        },
                    },
                }
            },
        }
    )
    assert bind_arguments({"rows": [{}]}, contract) == {"rows": [{"count": 0}]}
    assert secret_fields(contract) == ["rows"]
    for invalid in [
        [{"varName": "file", "varType": "File", "varDirection": 0}],
        {"type": "object", "properties": {"x": {"$ref": "https://untrusted.example/schema"}}},
        {"type": "object", "properties": {"x": {"type": "string", "format": "binary"}}},
    ]:
        with pytest.raises(WorkflowAccessError):
            schema(invalid)


def test_secret_dictionary_values_do_not_leak_parent_defaults():
    contract = schema(
        {
            "type": "object",
            "properties": {
                "credentials": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "writeOnly": True},
                    "default": {"account": "private-default"},
                }
            },
        }
    )
    assert secret_fields(contract) == ["credentials"]
    assert "private-default" not in json.dumps(contract)
