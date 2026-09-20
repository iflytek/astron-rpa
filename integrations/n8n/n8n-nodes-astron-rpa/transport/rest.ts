import { AstronError, object } from "../mapping/contracts";
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
      return {
        contractVersion: 1,
        profileSchemaVersion: 1,
        requiredClientProtocol: 1,
        durableIdempotency: true,
        operations: [
          "workflow_list",
          "workflow_get",
          "workflow_execute",
          "execution_get",
          "execution_cancel",
        ],
        client: { state: "unknown", protocol: 1, supportsCancel: false },
      };
    }
    if (name === "astron_workflow_execute") {
      const response = await this.request("workflows/execute-async", {
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
      });
      const data = object(response.data);
      if (typeof data.executionId !== "string")
        throw new AstronError("INVALID_EXECUTION_RESPONSE", true);
      return {
        executionId: data.executionId,
        projectId: args.projectId,
        version: args.version,
        status: "accepted",
        terminal: false,
        acceptedAt: null,
        finishedAt: null,
        startedAt: null,
        clientId: null,
        runId: null,
        cancelRequested: false,
        result: null,
        error: null,
        supportsCancel: false,
        resultVisibility: "json",
      };
    }
    if (name === "astron_execution_get") {
      const response = await this.request(
        `executions/${encodeURIComponent(String(args.executionId))}`,
      );
      const data = object(response.data);
      const execution = object(data.execution);
      const statusMap: Record<string, string> = {
        PENDING: "accepted",
        RUNNING: "running",
        COMPLETED: "succeeded",
        FAILED: "failed",
        CANCELLED: "cancelled",
        TIMEOUT: "timeout",
        UNKNOWN: "unknown",
      };
      const status = statusMap[String(execution.status)] ?? "unknown";
      const terminal = ["succeeded", "failed", "cancelled", "timeout"].includes(
        status,
      );
      return {
        executionId: String(execution.id),
        projectId: String(execution.project_id),
        version: Number(execution.version ?? 1),
        status,
        terminal,
        acceptedAt: null,
        finishedAt: execution.end_time ?? null,
        startedAt: execution.start_time ?? null,
        clientId: null,
        runId: null,
        cancelRequested: false,
        result: execution.result ?? null,
        error: execution.error
          ? { code: "EXECUTION_FAILED", message: "Workflow execution failed" }
          : null,
        supportsCancel: false,
        resultVisibility: "json",
      };
    }
    if (name === "astron_workflow_list") {
      const offset = Number(args.offset ?? 0);
      const limit = Number(args.limit ?? 100);
      const response = await this.request(
        `workflows/get?pageNo=${Math.floor(offset / limit) + 1}&pageSize=${limit}`,
      );
      const data = object(response.data);
      const records = Array.isArray(data.records) ? data.records : [];
      return {
        workflows: records.map((record) => object(record)),
        nextOffset: records.length === limit ? offset + limit : null,
      };
    }
    if (name === "astron_execution_cancel")
      throw new AstronError("REST_CANCEL_UNSUPPORTED");
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
