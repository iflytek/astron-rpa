/** Plan section numbers describe delivery order, not capability inheritance. */
export const CAPABILITY_GROUPS = {
  "json-data": { planSection: "4.1", title: "JSON and data workflows" },
  "browser-service": {
    planSection: "4.2",
    title: "Browser reads and service connections",
  },
  "office-file": { planSection: "4.3", title: "Office and file workflows" },
  "desktop-ui": { planSection: "4.4", title: "Desktop and UI automation" },
  "ai-dynamic-risk": {
    planSection: "4.5",
    title: "AI, dynamic code and high-risk workflows",
  },
} as const;

export type CapabilityGroup = keyof typeof CAPABILITY_GROUPS;

export interface ComponentCoverage {
  component: string;
  groups: readonly CapabilityGroup[];
  serviceReadOperations?: readonly string[];
  note: string;
}

/**
 * Operation-level classification inventory. A component can occur in several
 * peer groups according to its operations. A mixed workflow must satisfy every
 * applicable constraint; a group never inherits or grants another group. This catalog is deliberately kept in the integration package so
 * the node never imports Engine code.
 */
export const COMPONENT_COVERAGE: readonly ComponentCoverage[] = [
  {
    component: "astronverse-ai",
    groups: ["ai-dynamic-risk"],
    note: "AI and external-agent calls",
  },
  {
    component: "astronverse-browser",
    groups: ["browser-service", "office-file", "desktop-ui", "ai-dynamic-risk"],
    serviceReadOperations: [
      "BrowserElement.wait_element",
      "BrowserElement.similar",
      "BrowserElement.loop_similar",
      "BrowserElement.create_element",
      "BrowserElement.get_relative_element",
      "BrowserElement.element_operation",
      "BrowserElement.data_batch",
      "BrowserSoftware.get_current_obj",
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
    ],
    note: "Read-only queries and local browser context; generators and element handles stay inside the workflow. Attribute reads and single-page extraction require reviewed switches; export, scripts and page interaction remain outside this group",
  },
  {
    component: "astronverse-cua",
    groups: ["desktop-ui", "ai-dynamic-risk"],
    note: "Computer-use and screen interaction",
  },
  {
    component: "astronverse-database",
    groups: ["browser-service", "ai-dynamic-risk"],
    serviceReadOperations: [
      "Database.connect_database",
      "Database.query_sql",
      "Database.disconnect_database",
    ],
    note: "Reviewed fixed SQL with read-only credentials; connect/query/close stay in one workflow, connection objects never cross the JSON boundary",
  },
  {
    component: "astronverse-dataprocess",
    groups: ["json-data"],
    note: "Pure JSON and scalar processing",
  },
  {
    component: "astronverse-datatable",
    groups: ["json-data", "office-file"],
    note: "JSON-only tables remain 4.1; file-backed tables are 4.3",
  },
  {
    component: "astronverse-dialog",
    groups: ["desktop-ui"],
    note: "Interactive dialogs",
  },
  {
    component: "astronverse-email",
    groups: ["browser-service", "ai-dynamic-risk"],
    serviceReadOperations: ["Email.receive_email"],
    note: "Receive is admitted only with attachment-save and mark-as-read disabled; send/write is 4.5",
  },
  {
    component: "astronverse-encrypt",
    groups: ["json-data"],
    note: "Bounded JSON-safe transforms",
  },
  {
    component: "astronverse-enterprise",
    groups: ["browser-service", "office-file", "ai-dynamic-risk"],
    serviceReadOperations: ["Enterprise.get_shared_variable"],
    note: "Shared-variable reads are service reads; file operations are 4.3",
  },
  {
    component: "astronverse-excel",
    groups: ["office-file"],
    note: "Office runtime and files",
  },
  {
    component: "astronverse-input",
    groups: ["desktop-ui"],
    note: "Keyboard and mouse interaction",
  },
  {
    component: "astronverse-network",
    groups: ["browser-service", "office-file", "ai-dynamic-risk"],
    serviceReadOperations: [
      "Network.http_request",
      "Network.get_ftp_list",
      "Network.get_work_dir",
      "Network.ftp_create",
      "Network.ftp_close",
      "Network.change_working_dir",
    ],
    note: "HTTP read methods must not upload/save files; FTP reads are metadata-only, file transfer and writes belong to other capability groups",
  },
  {
    component: "astronverse-openapi",
    groups: ["office-file"],
    note: "Every current operation requires image/document paths; external service transport does not lower the file boundary",
  },
  {
    component: "astronverse-pdf",
    groups: ["office-file"],
    note: "Documents and binary files",
  },
  {
    component: "astronverse-report",
    groups: ["json-data"],
    note: "Structured logging/report output",
  },
  {
    component: "astronverse-script",
    groups: ["json-data", "ai-dynamic-risk"],
    note: "Only reviewed scripts can remain 4.1",
  },
  {
    component: "astronverse-smart",
    groups: ["ai-dynamic-risk"],
    note: "Dynamic code execution",
  },
  {
    component: "astronverse-software",
    groups: ["desktop-ui"],
    note: "Local program and process control",
  },
  {
    component: "astronverse-system",
    groups: ["office-file", "desktop-ui"],
    note: "Files, processes and desktop state",
  },
  {
    component: "astronverse-verifycode",
    groups: ["desktop-ui", "ai-dynamic-risk"],
    note: "Captcha and human/vision interaction",
  },
  {
    component: "astronverse-vision",
    groups: ["desktop-ui", "ai-dynamic-risk"],
    note: "Screen/image interaction",
  },
  {
    component: "astronverse-window",
    groups: ["desktop-ui"],
    note: "Window management",
  },
  {
    component: "astronverse-winelement",
    groups: ["desktop-ui"],
    note: "Desktop UI elements",
  },
  {
    component: "astronverse-word",
    groups: ["office-file"],
    note: "Office runtime and documents",
  },
] as const;

export const BROWSER_SERVICE_COMPONENTS = COMPONENT_COVERAGE.filter((entry) =>
  entry.groups.includes("browser-service"),
);
