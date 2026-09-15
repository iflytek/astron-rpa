"""Public JSON input contract; no expressions, remote references or file objects."""

import copy
import json
import re
from datetime import datetime

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from app.security.workflow_authorization import WorkflowAccessError

FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=ValueError)
def timezone_datetime(value):
    # jsonschema's optional RFC3339 dependency is not part of this deployment.
    if not isinstance(value, str):
        return True
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[Tt](?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:[Zz]|[+-](?:[01]\d|2[0-3]):[0-5]\d)",
        value,
    ):
        return False
    return datetime.fromisoformat(value.upper()).tzinfo is not None


TYPES = {
    "Str": "string",
    "Int": "integer",
    "Float": "number",
    "Bool": "boolean",
    "Boolean": "boolean",
    "List": "array",
    "Dict": "object",
    "Date": "string",
    "DateTime": "string",
    "Password": "string",
}
KEYWORDS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "description",
    "title",
    "default",
    "enum",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "uniqueItems",
    "items",
    "format",
    "writeOnly",
}


def validate_arguments(arguments, schema):
    try:
        json.dumps(arguments, allow_nan=False)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FORMATS).validate(arguments)
    except (ValueError, TypeError, ValidationError, SchemaError):
        raise WorkflowAccessError("INVALID_ARGUMENTS", "Arguments do not match the tool input schema") from None


def _property(source, depth=0):
    if not isinstance(source, dict) or set(source) - KEYWORDS or depth > 12:
        raise ValueError
    prop = copy.deepcopy(source)
    kind = prop.get("type")
    if isinstance(kind, list):
        if len(kind) != 2 or "null" not in kind:
            raise ValueError
        kind = next(item for item in kind if item != "null")
    if kind not in {"string", "integer", "number", "boolean", "array", "object"}:
        raise ValueError
    if prop.get("format") not in (None, "date", "date-time", "password"):
        raise ValueError
    if prop.get("writeOnly") or prop.get("format") == "password":
        prop["writeOnly"] = True
        prop.pop("default", None)
        prop.pop("enum", None)
    if kind == "object":
        prop["properties"] = {key: _property(value, depth + 1) for key, value in prop.get("properties", {}).items()}
        if isinstance(prop.get("additionalProperties"), dict):
            prop["additionalProperties"] = _property(prop["additionalProperties"], depth + 1)
        else:
            prop.setdefault("additionalProperties", False)
    if kind == "array" and "items" in prop:
        prop["items"] = _property(prop["items"], depth + 1)
    # A parent default/enum must not reintroduce a nested secret default.
    if secret_fields({"properties": {"value": prop}}):
        prop.pop("default", None)
        prop.pop("enum", None)
    if "default" in prop:
        Draft202012Validator(prop, format_checker=FORMATS).validate(prop["default"])
    return prop


def workflow_input_schema(workflow):
    try:
        parameters = json.loads(workflow.parameters) if workflow.parameters else []
        if isinstance(parameters, dict):
            if parameters.get("type") != "object":
                raise ValueError
            schema = _property(parameters)
            schema["additionalProperties"] = False
        elif isinstance(parameters, list):
            schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
            for param in parameters:
                if not isinstance(param, dict) or param.get("varDirection") not in (0, 1):
                    raise ValueError
                if param["varDirection"] != 0:
                    continue
                name = param.get("varName")
                if not isinstance(name, str) or not name or name in schema["properties"]:
                    raise ValueError
                kind = TYPES[param["varType"]]
                prop = {"type": kind, "description": param.get("varDescribe") or ""}
                if param.get("nullable") is True:
                    prop["type"] = [kind, "null"]
                if param["varType"] in ("Date", "DateTime"):
                    prop["format"] = "date" if param["varType"] == "Date" else "date-time"
                secret = param["varType"] == "Password"
                if secret:
                    prop["writeOnly"] = True
                if kind == "object":
                    prop["additionalProperties"] = True
                for keyword in ("enum", "minimum", "maximum", "minLength", "maxLength", "items", "properties"):
                    if keyword in param and not secret:
                        prop[keyword] = copy.deepcopy(param[keyword])
                default = param.get("varValue")
                has_default = not secret and default is not None and default != ""
                if default is None and param.get("nullable") and "varValue" in param:
                    has_default = True
                if has_default:
                    if isinstance(default, str) and kind != "string":
                        default = json.loads(default)
                    prop["default"] = default
                if param.get("required", not has_default):
                    schema["required"].append(name)
                schema["properties"][name] = _property(prop)
        else:
            raise ValueError
        Draft202012Validator.check_schema(schema)
        json.dumps(schema, allow_nan=False)
        return schema
    except (KeyError, TypeError, ValueError, SchemaError, ValidationError):
        raise WorkflowAccessError("UNSUPPORTED_PARAMETERS", "Workflow inputs require a supported JSON schema") from None


def bind_arguments(arguments, schema):
    """Apply declared defaults once, without coercing caller input values."""
    values = copy.deepcopy(arguments)
    if isinstance(values, dict):
        for key, prop in schema.get("properties", {}).items():
            if key not in values and "default" in prop:
                values[key] = copy.deepcopy(prop["default"])
            if key in values:
                values[key] = bind_arguments(values[key], prop)
    elif isinstance(values, list) and "items" in schema:
        values = [bind_arguments(item, schema["items"]) for item in values]
    validate_arguments(values, schema)
    return values


def secret_fields(schema):
    def contains(prop):
        return bool(
            prop.get("writeOnly")
            or any(contains(p) for p in prop.get("properties", {}).values())
            or (isinstance(prop.get("items"), dict) and contains(prop["items"]))
            or (isinstance(prop.get("additionalProperties"), dict) and contains(prop["additionalProperties"]))
        )

    return [key for key, prop in schema.get("properties", {}).items() if contains(prop)]


def workflow_secret_fields(workflow, schema):
    fields = set(secret_fields(schema))
    parameters = json.loads(workflow.parameters or "[]")
    if isinstance(parameters, list):
        fields.update(
            param["varName"]
            for param in parameters
            if isinstance(param, dict) and param.get("varType") == "Password" and param.get("varName")
        )
    return sorted(fields)
