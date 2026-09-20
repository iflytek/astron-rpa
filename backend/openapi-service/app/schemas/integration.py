"""Shared capability identifiers for external integration contracts."""

from typing import Literal

CAPABILITY_CLASSES = (
    "json-data",
    "browser-read",
    "service-http-read",
    "service-database-read",
    "service-mail-read",
    "service-openapi-read",
    "service-shared-read",
)

SERVICE_READ_CLASSES = frozenset(CAPABILITY_CLASSES[1:])
SERVICE_READ_OPERATIONS = {
    "browser-read": frozenset(
        {
            "BrowserElement.wait_element",
            "BrowserElement.similar",
            "BrowserElement.element_text",
            "BrowserElement.get_select",
            "BrowserElement.get_checked",
            "BrowserElement.get_table",
            "BrowserElement.element_exist",
            "BrowserSoftware.get_cookies",
            "BrowserSoftware.wait_web_load",
            "BrowserSoftware.get_current_url",
            "BrowserSoftware.get_current_title",
            "BrowserSoftware.get_current_tab_id",
        }
    ),
    "service-http-read": frozenset(
        {"Network.http_request", "Network.get_ftp_list", "Network.get_work_dir"}
    ),
    "service-database-read": frozenset({"Database.query_sql"}),
    "service-mail-read": frozenset({"Email.receive_email"}),
    "service-openapi-read": frozenset(),
    "service-shared-read": frozenset({"Enterprise.get_shared_variable"}),
}
CapabilityClass = Literal[
    "json-data",
    "browser-read",
    "service-http-read",
    "service-database-read",
    "service-mail-read",
    "service-openapi-read",
    "service-shared-read",
]
