import { randomUUID } from "node:crypto";

export interface Correlation {
  n8nExecutionId: string;
  itemIndex: number;
  report?: (event: TransportDiagnostic) => void;
}

export interface TransportDiagnostic {
  event: "astron_transport_failure";
  transport: "mcp" | "rest" | "file";
  targetHost: string;
  traceId: string;
  errorType: string;
  n8nExecutionId?: string;
  itemIndex?: number;
}

/** Log only bounded diagnostics, including failures that never reach the server. */
export async function observedFetch(
  fetcher: typeof fetch,
  url: Parameters<typeof fetch>[0],
  init: RequestInit,
  context: Correlation | undefined,
  transport: TransportDiagnostic["transport"],
): Promise<Response> {
  const correlation = correlationHeaders(context);
  const headers = new Headers(init.headers);
  Object.entries(correlation).forEach(([key, value]) =>
    headers.set(key, value),
  );
  const report = (errorType: string) => {
    try {
      context?.report?.({
        event: "astron_transport_failure",
        transport,
        targetHost: new URL(url instanceof Request ? url.url : String(url))
          .hostname,
        traceId: correlation["X-Request-ID"],
        errorType,
        ...(correlation["X-N8N-Execution-ID"]
          ? { n8nExecutionId: correlation["X-N8N-Execution-ID"] }
          : {}),
        ...(correlation["X-N8N-Item-Index"]
          ? { itemIndex: Number(correlation["X-N8N-Item-Index"]) }
          : {}),
      });
    } catch {
      // Diagnostics must never change the dispatch/uncertainty contract.
    }
  };
  let response: Response;
  try {
    response = await fetcher(url, { ...init, headers });
  } catch (error) {
    const outer = error && typeof error === "object" ? error : {};
    const cause =
      "cause" in outer && outer.cause && typeof outer.cause === "object"
        ? outer.cause
        : outer;
    const code = "code" in cause ? cause.code : undefined;
    const name = "name" in outer ? outer.name : undefined;
    report(
      [
        "CERT_HAS_EXPIRED",
        "ERR_TLS_CERT_ALTNAME_INVALID",
        "DEPTH_ZERO_SELF_SIGNED_CERT",
        "UNABLE_TO_VERIFY_LEAF_SIGNATURE",
        "SELF_SIGNED_CERT_IN_CHAIN",
        "UNABLE_TO_GET_ISSUER_CERT_LOCALLY",
      ].includes(String(code))
        ? "TLS_ERROR"
        : ["TimeoutError", "AbortError"].includes(String(name)) ||
            [
              "ETIMEDOUT",
              "UND_ERR_CONNECT_TIMEOUT",
              "UND_ERR_HEADERS_TIMEOUT",
              "UND_ERR_BODY_TIMEOUT",
            ].includes(String(code))
          ? "TIMEOUT"
          : [
                "ENOTFOUND",
                "EAI_AGAIN",
                "ECONNREFUSED",
                "ECONNRESET",
                "ENETUNREACH",
                "EHOSTUNREACH",
              ].includes(String(code))
            ? "NETWORK_ERROR"
            : "UNCONFIRMED",
    );
    throw error;
  }
  if (!response.ok && response.status !== 405)
    report(
      [401, 403, 429].includes(response.status)
        ? `HTTP_${response.status}`
        : "HTTP_ERROR",
    );
  return response;
}

/** Diagnostics only: never part of authorization or the idempotency identity. */
export function correlationHeaders(
  context?: Correlation,
): Record<string, string> {
  return {
    "X-Request-ID": randomUUID(),
    ...(context && /^[A-Za-z0-9_.:-]{1,96}$/.test(context.n8nExecutionId)
      ? { "X-N8N-Execution-ID": context.n8nExecutionId }
      : {}),
    ...(context &&
    Number.isSafeInteger(context.itemIndex) &&
    context.itemIndex >= 0
      ? { "X-N8N-Item-Index": String(context.itemIndex) }
      : {}),
  };
}
