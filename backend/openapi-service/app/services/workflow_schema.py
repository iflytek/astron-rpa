"""Public JSON input contract; no expressions, remote references or file objects."""

import copy
import json
import math
import re
from datetime import datetime

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from app.security.workflow_authorization import WorkflowAccessError

FORMATS = FormatChecker()

# The data-workflow contract is deliberately bounded before values reach MCP,
# n8n history or the desktop client. Keep these values in one place so the
# server and node can expose and test the same limits.
JSON_LIMITS = {
    "maxBytes": 1_048_576,
    "maxDepth": 12,
    "maxObjectProperties": 200,
    "maxArrayItems": 1_000,
    "maxStringLength": 100_000,
}


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
    "minProperties",
    "maxProperties",
    "items",
    "format",
    "writeOnly",
}


def validate_json_value(value, *, require_object=False, limits=None):
    """Bound plain JSON before copying, validation, serialization or persistence."""
    limits = JSON_LIMITS if limits is None else limits
    invalid = "Arguments do not match the JSON input schema"
    if require_object and type(value) is not dict:
        raise WorkflowAccessError("INVALID_ARGUMENTS", invalid)
    budget = 0

    def visit(current, depth=0):
        nonlocal budget
        kind = type(current)
        if kind in (dict, list) and depth > limits["maxDepth"]:
            raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON nesting exceeds the maximum depth")
        if current is None or kind is bool:
            budget += len(json.dumps(current))
        elif kind in (int, float):
            unsafe_float = kind is float and (
                not math.isfinite(current) or (current.is_integer() and abs(current) > 9_007_199_254_740_991)
            )
            if (kind is int and abs(current) > 9_007_199_254_740_991) or unsafe_float:
                raise WorkflowAccessError("INVALID_ARGUMENTS", invalid)
            budget += len(str(current))
        elif kind is str:
            # Unicode scalar values match Array.from(string).length in the node.
            if len(current) > limits["maxStringLength"]:
                raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON string exceeds the maximum length")
            try:
                budget += len(current.encode("utf-8"))
            except UnicodeEncodeError:
                raise WorkflowAccessError("INVALID_ARGUMENTS", invalid) from None
        elif kind is dict:
            if len(current) > limits["maxObjectProperties"]:
                raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON object has too many properties")
            budget += 2
            for key, child in current.items():
                if type(key) is not str:
                    raise WorkflowAccessError("INVALID_ARGUMENTS", invalid)
                visit(key, depth + 1)
                visit(child, depth + 1)
        elif kind is list:
            if len(current) > limits["maxArrayItems"]:
                raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON array has too many items")
            budget += 2
            for child in current:
                visit(child, depth + 1)
        else:
            raise WorkflowAccessError("INVALID_ARGUMENTS", invalid)
        if budget > limits["maxBytes"]:
            raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON value exceeds the maximum size")

    visit(value)
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > limits["maxBytes"]:
        raise WorkflowAccessError("JSON_LIMIT_EXCEEDED", "JSON value exceeds the maximum size")
    return value


def validate_arguments(arguments, schema):
    try:
        validate_json_value(arguments, require_object=True)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FORMATS).validate(arguments)
    except (ValueError, TypeError, RecursionError, ValidationError, SchemaError):
        raise WorkflowAccessError("INVALID_ARGUMENTS", "Arguments do not match the tool input schema") from None


def _property(source, depth=0):
    if not isinstance(source, dict) or set(source) - KEYWORDS or depth > JSON_LIMITS["maxDepth"]:
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
                for keyword in (
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
                    "minProperties",
                    "maxProperties",
                    "items",
                    "properties",
                    "additionalProperties",
                ):
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
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError, SchemaError, ValidationError):
        raise WorkflowAccessError("UNSUPPORTED_PARAMETERS", "Workflow inputs require a supported JSON schema") from None


def bind_arguments(arguments, schema):
    """Apply defaults once, validate once, and never coerce input values."""

    def bind(value, prop):
        if isinstance(value, dict):
            properties = prop.get("properties", {})
            extra = prop.get("additionalProperties")
            for key, child_schema in properties.items():
                if key not in value and "default" in child_schema:
                    value[key] = copy.deepcopy(child_schema["default"])
                if key in value:
                    value[key] = bind(value[key], child_schema)
            if isinstance(extra, dict):
                for key in value.keys() - properties.keys():
                    value[key] = bind(value[key], extra)
        elif isinstance(value, list) and "items" in prop:
            value = [bind(item, prop["items"]) for item in value]
        return value

    values = bind(copy.deepcopy(arguments), schema)
    validate_arguments(values, schema)
    return values


def data_output_schema(source):
    """Optional JSON result schema, without references, defaults or secret output declarations."""
    if source is None:
        return None
    try:
        result = _property(source)
        Draft202012Validator.check_schema(result)

        def check(prop):
            if "default" in prop or prop.get("writeOnly") or prop.get("format") == "password":
                raise ValueError
            for child in prop.get("properties", {}).values():
                check(child)
            for key in ("items", "additionalProperties"):
                if isinstance(prop.get(key), dict):
                    check(prop[key])

        check(source)
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > JSON_LIMITS["maxBytes"]:
            raise ValueError
        return result
    except (KeyError, TypeError, ValueError, RecursionError, SchemaError, ValidationError):
        raise WorkflowAccessError("UNSUPPORTED_OUTPUT_SCHEMA", "Output requires a supported JSON schema") from None


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
