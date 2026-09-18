import json

import pytest

from app.models.workflow import Workflow
from app.security.workflow_authorization import WorkflowAccessError
from app.services.workflow_schema import (
    JSON_LIMITS,
    bind_arguments,
    data_output_schema,
    secret_fields,
    validate_json_value,
    workflow_input_schema,
)


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


def test_json_data_limits_are_explicit_and_fail_closed():
    assert JSON_LIMITS == {
        "maxBytes": 1_048_576,
        "maxDepth": 12,
        "maxObjectProperties": 200,
        "maxArrayItems": 1_000,
        "maxStringLength": 100_000,
    }
    validate_json_value({"value": "ok"}, require_object=True)
    with pytest.raises(WorkflowAccessError) as error:
        validate_json_value({"values": [0] * (JSON_LIMITS["maxArrayItems"] + 1)}, require_object=True)
    assert error.value.code == "JSON_LIMIT_EXCEEDED"
    with pytest.raises(WorkflowAccessError) as error:
        validate_json_value({"value": "x" * (JSON_LIMITS["maxStringLength"] + 1)}, require_object=True)
    assert error.value.code == "JSON_LIMIT_EXCEEDED"
    nested = value = {}
    for _ in range(JSON_LIMITS["maxDepth"] + 1):
        value["next"] = {}
        value = value["next"]
    with pytest.raises(WorkflowAccessError) as error:
        validate_json_value(nested, require_object=True)
    assert error.value.code == "JSON_LIMIT_EXCEEDED"
    with pytest.raises(WorkflowAccessError) as error:
        validate_json_value({"value": float("nan")}, require_object=True)
    assert error.value.code == "INVALID_ARGUMENTS"


def test_output_schema_rejects_defaults_secrets_and_references():
    output = data_output_schema(
        {
            "type": "object",
            "properties": {"count": {"type": "integer"}},
            "additionalProperties": False,
        }
    )
    assert output["properties"]["count"]["type"] == "integer"
    for invalid in [
        {"type": "object", "properties": {"value": {"type": "string", "default": "x"}}},
        {"type": "object", "properties": {"value": {"type": "string", "writeOnly": True}}},
        {"type": "object", "properties": {"value": {"$ref": "https://example.invalid/schema"}}},
    ]:
        with pytest.raises(WorkflowAccessError, match="supported JSON schema"):
            data_output_schema(invalid)


def test_output_schema_is_bounded_before_persistence():
    with pytest.raises(WorkflowAccessError, match="supported JSON schema"):
        data_output_schema({"type": "string", "description": "x" * 1_048_577})
