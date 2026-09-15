from astronverse.executor.external_values import json_value
from astronverse.executor.utils.utils import str_to_list_if_possible


def parse_run_params(run_params, parser):
    """Keep native JSON numbers/bools; preserve the legacy expression path."""
    values = {}
    if not isinstance(run_params, list):
        return values
    for item in run_params:
        name = item.get("varName")
        value = item.get("varValue")
        if item.get("encoding") == "json":
            # Managed remote inputs are native JSON literals, never expressions.
            values[name] = json_value(value)
            continue
        if type(value) in (int, float, bool):
            values[name] = value
            continue
        param = parser.parse_param(
            {"value": str_to_list_if_possible(value), "types": item.get("varType"), "name": name}
        )
        expression = param.show_value()
        # External expressions cannot reference flow variables (legacy behavior).
        values[name] = eval(expression, {}, {}) if expression else ""  # noqa: S307 -- retain legacy expression support
    return values
