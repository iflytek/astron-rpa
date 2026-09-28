import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { AstronError, object } from "../mapping/contracts";

export interface Connection {
  endpoint: string;
  apiKey: string;
  protocol: string;
}
export function endpoint(raw: string): URL {
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw new AstronError("INVALID_ENDPOINT");
  }
  if (
    url.protocol !== "https:" ||
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    !/\/mcp\/?$/.test(url.pathname) ||
    url.pathname.includes("//") ||
    /\/mcp\/mcp\/?$/.test(url.pathname)
  ) {
    throw new AstronError("INVALID_ENDPOINT");
  }
  url.pathname = url.pathname.replace(/\/?$/, "/");
  return url;
}

export class McpConnection {
  private client = new Client({
    name: "n8n-nodes-astron-rpa",
    version: "0.1.0-dev.2",
  });
  private transport: StreamableHTTPClientTransport;
  constructor(
    connection: Connection,
    private readonly timeout: number,
    fetcher: typeof fetch = fetch,
  ) {
    if (connection.protocol !== "2025-11-25")
      throw new AstronError("PROTOCOL_UNSUPPORTED");
    if (!connection.apiKey.trim())
      throw new AstronError("AUTHENTICATION_FAILED");
    this.transport = new StreamableHTTPClientTransport(
      endpoint(connection.endpoint),
      {
        requestInit: {
          headers: { Authorization: `Bearer ${connection.apiKey}` },
        },
        // Refuse every redirect, including same-origin changes to the configured path.
        fetch: async (url, init) => {
          try {
            const response = await fetcher(url, {
              ...init,
              redirect: "error",
              signal: AbortSignal.any([
                ...(init?.signal ? [init.signal] : []),
                AbortSignal.timeout(timeout),
              ]),
            });
            if (!response.ok && response.status !== 405) {
              throw new AstronError(
                response.status === 401
                  ? "AUTHENTICATION_FAILED"
                  : response.status === 403
                    ? "PERMISSION_DENIED"
                    : "HTTP_ERROR",
                response.status >= 500,
              );
            }
            return response;
          } catch (error) {
            if (error instanceof AstronError) throw error;
            throw new AstronError("TRANSPORT_UNCONFIRMED", true);
          }
        },
      },
    );
  }
  async connect(): Promise<void> {
    try {
      await this.client.connect(this.transport, { timeout: this.timeout });
      if (this.transport.protocolVersion !== "2025-11-25")
        throw new AstronError("PROTOCOL_UNSUPPORTED");
    } catch (error) {
      throw safeError(error);
    }
  }
  async call(
    name: string,
    args: Record<string, unknown>,
  ): Promise<Record<string, unknown>> {
    try {
      const result = await this.client.callTool(
        { name, arguments: args },
        undefined,
        { timeout: this.timeout },
      );
      let payload: unknown = result.structuredContent;
      if (payload === undefined) {
        const content = result.content;
        if (
          !Array.isArray(content) ||
          content.length !== 1 ||
          content[0].type !== "text"
        )
          throw new AstronError("INVALID_RESPONSE");
        try {
          payload = JSON.parse(content[0].text as string);
        } catch {
          throw new AstronError("INVALID_RESPONSE");
        }
      }
      const value = object(payload);
      if (result.isError) {
        const code = object(value.error).code;
        // Never copy remote messages, arguments or stack traces to n8n errors.
        const safeCode =
          typeof code === "string" && /^[A-Z_]{3,64}$/.test(code)
            ? code
            : "MCP_TOOL_ERROR";
        throw new AstronError(
          safeCode,
          ["INTERNAL_ERROR", "MCP_TOOL_ERROR"].includes(safeCode),
        );
      }
      return value;
    } catch (error) {
      if (error instanceof AstronError && error.code === "INVALID_RESPONSE")
        throw new AstronError(error.code, true);
      throw safeError(error);
    }
  }
  async listTools(): Promise<string[]> {
    try {
      return (
        await this.client.listTools({}, { timeout: this.timeout })
      ).tools.map((tool) => tool.name);
    } catch (error) {
      throw safeError(error);
    }
  }
  async close(): Promise<void> {
    await this.client.close().catch(() => undefined);
  }
}

export function safeError(error: unknown): AstronError {
  return error instanceof AstronError
    ? error
    : new AstronError("MCP_REQUEST_UNCONFIRMED", true);
}

export async function withMcp<T>(
  connection: Connection,
  timeout: number,
  action: (client: McpConnection) => Promise<T>,
): Promise<T> {
  const client = new McpConnection(connection, timeout);
  try {
    await client.connect();
    return await action(client);
  } finally {
    await client.close();
  }
}
