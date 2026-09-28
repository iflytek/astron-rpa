"""Read constraints for administrator-reviewed, version-bound service workflows.

The review describes fixed component arguments and direct workflow-input bindings.
It is not a workflow compiler or a sandbox for untrusted Python. Reviewers must
verify those bindings against the published workflow and use read-only service
accounts; dynamic SQL and undeclared parameter transformations are not admitted.
"""

import re

from app.security.workflow_authorization import WorkflowAccessError

# Only arguments which can cross this capability's boundary are described here.
RULES = {
    "Network.http_request": {"request_type": ("get", "head"), "file_path": ("",), "save_type": ("no",)},
    "Email.receive_email": {"save_attachment_flag": (False,), "mask_as_read_flag": (False,)},
    "BrowserElement.get_table": {"to_excel": (False,)},
    "BrowserElement.data_batch": {
        "to_excel": (False,),
        "is_save_to_data_table": (False,),
        "multi_page": (False,),
        "page_count": (1,),
    },
    "BrowserElement.element_operation": {"operation_type": ("get",)},
    "Database.query_sql": {"sql": None},
}


def _valid_value(value, allowed):
    if allowed is not None:
        return any(type(value) is type(option) and value == option for option in allowed)
    if not isinstance(value, str) or not value.strip() or len(value) > 100_000:
        return False
    # A conservative check of fixed reviewed SQL, not a general SQL security parser.
    sql = value.strip().removesuffix(";")
    if any(token in sql for token in (";", "--", "/*", "#")):
        return False
    sql = re.sub(r"'(?:''|[^'])*'", "''", sql)
    return bool(re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE)) and not re.search(
        r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|INTO|CALL|EXEC|COPY|ATTACH|PRAGMA|LOCK)\b",
        sql,
        re.IGNORECASE,
    )


def validate_read_review(review: dict | None, operations: list[str], schema: dict, params: dict | None = None):
    def reject():
        raise WorkflowAccessError("READ_CONSTRAINT_INVALID", "Workflow read constraints are missing or invalid")

    if not isinstance(review, dict) or set(review) != {
        "version",
        "operationInputs",
        "readOnlyConnections",
        "boundedResources",
    }:
        reject()
    if type(review["version"]) is not int or review["version"] != 1:
        reject()
    if review["readOnlyConnections"] is not True or review["boundedResources"] is not True:
        reject()
    inputs = review["operationInputs"]
    if not isinstance(inputs, dict) or set(inputs) != set(operations):
        reject()
    for operation in operations:
        rules = RULES.get(operation, {})
        instances = inputs[operation]
        if not isinstance(instances, list):
            instances = [instances]
        if not instances or len(instances) > 100:
            reject()
        for values in instances:
            if not isinstance(values, dict) or set(values) != set(rules):
                reject()
            for argument, allowed in rules.items():
                value = values[argument]
                if isinstance(value, dict):
                    # SQL stays fixed in the reviewed workflow; values must not be
                    # concatenated from caller input. No credential is part of this review.
                    if argument == "sql" or set(value) != {"parameter"} or not isinstance(value["parameter"], str):
                        reject()
                    name = value["parameter"]
                    prop = schema.get("properties", {}).get(name)
                    if not isinstance(prop, dict) or not prop.get("enum"):
                        reject()
                    if not all(_valid_value(item, allowed) for item in prop["enum"]):
                        reject()
                    if params is None:
                        continue
                    value = params.get(name)
                if not _valid_value(value, allowed):
                    reject()
