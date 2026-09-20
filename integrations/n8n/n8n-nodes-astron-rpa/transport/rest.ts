import { AstronError, object, snapshot } from "../mapping/contracts";
import type { Connection } from "./mcp";

type Fetcher = typeof fetch;

export class RestConnection {
  private readonly base: URL;

  constructor(
    private readonly connection: Connection,
    private readonly timeout: number,
    private readonly fetcher: Fetcher = fetch,
  ) {
    const endpoint = new URL(connection.endpoint);
    endpoint.pathname = endpoint.pathname.replace(/mcp\/?$/, "");
    endpoint.search = "";
    endpoint.hash = "";
    if (endpoint.protocol !== "https:" || !endpoint.pathname.endsWith("/"))
      throw new AstronError("INVALID_ENDPOINT");
    this.base = endpoint;
  }

  async connect(): Promise<void> {
    if (!this.connection.apiKey.trim())
      throw new AstronError("AUTHENTICATION_FAILED");
  }

  private async request(
    path: string,
    init: RequestInit = {},
  ): Promise<Record<string, unknown>> {
    const url = new URL(path.replace(/^\//, ""), this.base);
    const response = await this.fetcher(url, {
      ...init,
      redirect: "error",
      headers: {
        Authorization: `Bearer ${this.connection.apiKey}`,
        Accept: "application/json",
        ...(init.headers ?? {}),
      },
      signal: AbortSignal.any([
        ...(init.signal ? [init.signal] : []),
        AbortSignal.timeout(this.timeout),
      ]),
    }).catch((error) => {
      if (error instanceof AstronError) throw error;
      throw new AstronError("TRANSPORT_UNCONFIRMED", true);
    });
    if (!response.ok) {
      // Preserve the shared contract's safe business code, never remote messages.
      const payload: unknown = await response.json().catch(() => null);
      const detail =
        payload && typeof payload === "object" && "detail" in payload
          ? payload.detail
          : null;
      const code =
        detail && typeof detail === "object" && "code" in detail
          ? detail.code
          : null;
      if (typeof code === "string" && /^[A-Z_]{3,64}$/.test(code))
        throw new AstronError(
          code,
          response.status >= 500 &&
            !["CLIENT_OFFLINE", "CLIENT_CAPABILITY_UNCONFIRMED"].includes(code),
        );
      throw new AstronError(
        response.status === 401
          ? "AUTHENTICATION_FAILED"
          : response.status === 403
            ? "PERMISSION_DENIED"
            : response.status >= 500
              ? "REST_REQUEST_UNCONFIRMED"
              : "REST_REQUEST_FAILED",
        response.status >= 500,
      );
    }
    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new AstronError("INVALID_RESPONSE", true);
    }
    const result = object(payload);
    if (result.code !== undefined && result.code !== "0000")
      throw new AstronError("REST_REQUEST_FAILED");
    return result;
  }

  async call(
    name: string,
    args: Record<string, unknown>,
  ): Promise<Record<string, unknown>> {
    if (name === "astron_integration_get") {
      return object((await this.request("workflows/integration")).data);
    }
    if (name === "astron_workflow_execute") {
      const response = await this.request(
        "workflows/execute-async?contract=1",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: args.projectId,
            version: args.version,
            params: args.params ?? {},
            idempotency_key: args.idempotencyKey,
            execution_timeout: args.executionTimeout,
            profile_revision: args.profileRevision,
            capability_class: args.capabilityClass,
          }),
        },
      );
      return snapshot(object(response.data).snapshot, {
        projectId: String(args.projectId),
        version: Number(args.version),
      });
    }
    if (name === "astron_execution_get" || name === "astron_execution_cancel") {
      const executionId = String(args.executionId);
      const cancelling = name === "astron_execution_cancel";
      const response = await this.request(
        `executions/${encodeURIComponent(executionId)}${cancelling ? "/cancel" : "?contract=1"}`,
        cancelling ? { method: "POST" } : {},
      );
      return snapshot(object(response.data).snapshot, { executionId });
    }
    throw new AstronError("REST_OPERATION_UNSUPPORTED");
  }

  async close(): Promise<void> {}
}

export async function withRest<T>(
  connection: Connection,
  timeout: number,
  action: (client: RestConnection) => Promise<T>,
): Promise<T> {
  const client = new RestConnection(connection, timeout);
  try {
    await client.connect();
    return await action(client);
  } finally {
    await client.close();
  }
}
