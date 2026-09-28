import type { ICredentialType, INodeProperties } from "n8n-workflow";

export class AstronRpaApi implements ICredentialType {
  name = "astronRpaApi";
  displayName = "AstronRPA MCP API";
  documentationUrl = "https://github.com/iflytek/astron-rpa";
  properties: INodeProperties[] = [
    {
      displayName: "MCP Endpoint",
      name: "endpoint",
      type: "string",
      default: "",
      required: true,
      placeholder: "https://rpa.example.com/api/rpa-openapi/mcp/",
      description:
        "HTTPS MCP endpoint; credentials in URLs and redirects are refused",
    },
    {
      displayName: "API Key",
      name: "apiKey",
      type: "string",
      typeOptions: { password: true },
      default: "",
      required: true,
    },
    {
      displayName: "MCP Protocol",
      name: "protocol",
      type: "options",
      options: [{ name: "2025-11-25", value: "2025-11-25" }],
      default: "2025-11-25",
    },
  ];
}
