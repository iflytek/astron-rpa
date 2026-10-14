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
  officeFileOperations?: readonly string[];
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
    officeFileOperations: [
      "BrowserElement.create_element",
      "BrowserElement.data_batch",
      "BrowserElement.get_table",
      "BrowserElement.position_screenshot",
      "BrowserElement.screenshot",
      "BrowserElement.wait_element",
      "BrowserSoftware.download_web_file",
      "BrowserSoftware.get_current_obj",
      "BrowserSoftware.get_current_url",
      "BrowserSoftware.screenshot",
      "BrowserSoftware.upload_web_file",
      "BrowserSoftware.wait_web_load",
    ],
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
    component: "astronverse-control",
    groups: ["json-data"],
    note: "Control-flow markers; nested operations still require their own capability review. This entry grants no service-read operations",
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
    officeFileOperations: [
      "DataTable.export_data_table_to_file",
      "DataTable.import_data_table_from_file",
    ],
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
    officeFileOperations: ["Email.receive_email"],
    groups: ["browser-service", "office-file", "ai-dynamic-risk"],
    serviceReadOperations: ["Email.receive_email"],
    note: "Service reads disable attachment saving and marking as read; managed attachment files require an Office/file review. Sending remains a high-risk operation",
  },
  {
    component: "astronverse-encrypt",
    groups: ["json-data"],
    note: "Bounded JSON-safe transforms",
  },
  {
    component: "astronverse-enterprise",
    officeFileOperations: [
      "Enterprise.download_from_sharefolder",
      "Enterprise.upload_to_sharefolder",
    ],
    groups: ["browser-service", "office-file", "ai-dynamic-risk"],
    serviceReadOperations: ["Enterprise.get_shared_variable"],
    note: "Shared-variable reads are service reads; file operations are 4.3",
  },
  {
    component: "astronverse-excel",
    officeFileOperations: [
      "Excel.add_excel_worksheet",
      "Excel.clear_excel_content",
      "Excel.close_excel",
      "Excel.copy_excel_worksheet",
      "Excel.create_excel",
      "Excel.create_excel_comment",
      "Excel.delete_excel_cell",
      "Excel.delete_excel_comment",
      "Excel.delete_excel_worksheet",
      "Excel.design_cell_type",
      "Excel.edit_excel",
      "Excel.excel_get_cell_color",
      "Excel.excel_number_to_text",
      "Excel.excel_set_col_width",
      "Excel.excel_set_row_height",
      "Excel.excel_text_to_number",
      "Excel.get_excel_col_num",
      "Excel.get_excel_first_available_col",
      "Excel.get_excel_first_available_row",
      "Excel.get_excel_row_num",
      "Excel.get_excel_worksheet_names",
      "Excel.insert_excel_row_or_column",
      "Excel.insert_formula",
      "Excel.insert_pic",
      "Excel.loop_excel_content",
      "Excel.merge_split_excel_cell",
      "Excel.move_excel_worksheet",
      "Excel.open_excel",
      "Excel.read_excel",
      "Excel.rename_excel_worksheet",
      "Excel.save_excel",
      "Excel.search_and_replace_excel_content",
    ],
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
    officeFileOperations: [
      "Network.ftp_close",
      "Network.ftp_create",
      "Network.ftp_download",
      "Network.ftp_upload",
      "Network.http_download",
      "Network.http_request",
    ],
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
    officeFileOperations: [
      "OpenApi.business_license",
      "OpenApi.common_ocr",
      "OpenApi.id_card",
      "OpenApi.taxi_ticket",
      "OpenApi.train_ticket",
      "OpenApi.vat_invoice",
    ],
    groups: ["office-file"],
    note: "Every current operation requires image/document paths; external service transport does not lower the file boundary",
  },
  {
    component: "astronverse-pdf",
    officeFileOperations: [
      "PDF.convert_img_to_pdf",
      "PDF.convert_pdf_to_img",
      "PDF.extract_forms_from_pdf",
      "PDF.extract_pdf_file",
      "PDF.get_pages_num",
      "PDF.get_pdf_images",
      "PDF.get_pdf_text",
      "PDF.merge_pdf_files",
    ],
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
    officeFileOperations: [
      "Compress.compress",
      "Compress.uncompress",
      "File.file_copy",
      "File.file_create",
      "File.file_delete",
      "File.file_exist",
      "File.file_info",
      "File.file_move",
      "File.file_read",
      "File.file_rename",
      "File.file_search",
      "File.file_wait_status",
      "File.file_write",
      "File.get_file_encoding_type",
      "File.get_file_list",
      "Folder.folder_clear",
      "Folder.folder_copy",
      "Folder.folder_create",
      "Folder.folder_delete",
      "Folder.folder_exist",
      "Folder.folder_move",
      "Folder.folder_rename",
      "Folder.get_folder_list",
    ],
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
    officeFileOperations: [
      "Docx.close_docx",
      "Docx.convert_format",
      "Docx.create_comment",
      "Docx.create_docx",
      "Docx.delete",
      "Docx.delete_comment",
      "Docx.get_cursor_position",
      "Docx.insert_docx",
      "Docx.insert_hyperlink",
      "Docx.insert_img",
      "Docx.insert_sep",
      "Docx.insert_table",
      "Docx.move_cursor",
      "Docx.open_docx",
      "Docx.read_docx",
      "Docx.read_table",
      "Docx.replace",
      "Docx.save_docx",
      "Docx.select_text",
    ],
    groups: ["office-file"],
    note: "Office runtime and documents",
  },
] as const;

export const BROWSER_SERVICE_COMPONENTS = COMPONENT_COVERAGE.filter((entry) =>
  entry.groups.includes("browser-service"),
);

export const OFFICE_FILE_OPERATIONS = new Set(
  COMPONENT_COVERAGE.flatMap((entry) => entry.officeFileOperations ?? []),
);
