import type { IDataObject } from "n8n-workflow";

export class AstronError extends Error {
  constructor(
    public readonly code: string,
    public readonly uncertain = false,
  ) {
    super(code);
  }
}

export const JSON_LIMITS = {
  maxBytes: 1_048_576,
  maxDepth: 12,
  maxObjectProperties: 200,
  maxArrayItems: 1_000,
  maxStringLength: 100_000,
} as const;

export function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new AstronError("INVALID_RESPONSE");
  return value as Record<string, unknown>;
}

export function jsonObject(value: unknown): IDataObject {
  if (typeof value === "string") {
    try {
      value = JSON.parse(value);
    } catch {
      throw new AstronError("INVALID_ARGUMENTS");
    }
  }
  const record = object(value);
  // JSON inputs only, without implicit stringification or non-finite numbers.
  const ancestors = new WeakSet<object>();
  const visit = (v: unknown, depth = 0): void => {
    if (v === null || typeof v === "boolean") return;
    if (typeof v === "string") {
      if (Array.from(v).length > JSON_LIMITS.maxStringLength)
        throw new AstronError("JSON_LIMIT_EXCEEDED");
      return;
    }
    if (
      typeof v === "number" &&
      Number.isFinite(v) &&
      (!Number.isInteger(v) || Number.isSafeInteger(v))
    )
      return;
    if (Array.isArray(v)) {
      if (v.length > JSON_LIMITS.maxArrayItems || depth > JSON_LIMITS.maxDepth)
        throw new AstronError("JSON_LIMIT_EXCEEDED");
      if (ancestors.has(v)) throw new AstronError("INVALID_ARGUMENTS");
      ancestors.add(v);
      v.forEach((item) => visit(item, depth + 1));
      ancestors.delete(v);
      return;
    }
    if (
      v &&
      typeof v === "object" &&
      Object.getPrototypeOf(v) === Object.prototype
    ) {
      if (
        Object.keys(v).length > JSON_LIMITS.maxObjectProperties ||
        depth > JSON_LIMITS.maxDepth
      )
        throw new AstronError("JSON_LIMIT_EXCEEDED");
      if (ancestors.has(v)) throw new AstronError("INVALID_ARGUMENTS");
      ancestors.add(v);
      Object.keys(v).forEach((key) => visit(key));
      Object.values(v).forEach((item) => visit(item, depth + 1));
      ancestors.delete(v);
      return;
    }
    throw new AstronError("INVALID_ARGUMENTS");
  };
  visit(record);
  const encoded = JSON.stringify(record);
  if (
    encoded === undefined ||
    new TextEncoder().encode(encoded).length > JSON_LIMITS.maxBytes
  )
    throw new AstronError("JSON_LIMIT_EXCEEDED");
  return JSON.parse(JSON.stringify(record)) as IDataObject;
}

export interface Snapshot extends IDataObject {
  executionId: string;
  projectId: string;
  version: number;
  status: string;
  terminal: boolean;
}
const terminalStates = new Set(["succeeded", "failed", "cancelled", "timeout"]);
const states = new Set([...terminalStates, "accepted", "running", "unknown"]);
export function snapshot(
  value: unknown,
  expected?: { executionId?: string; projectId?: string; version?: number },
): Snapshot {
  const v = object(value);
  if (
    typeof v.executionId !== "string" ||
    !/^[a-f0-9-]{36}$/i.test(v.executionId) ||
    typeof v.projectId !== "string" ||
    !Number.isInteger(v.version) ||
    typeof v.status !== "string" ||
    !states.has(v.status) ||
    v.terminal !== terminalStates.has(v.status) ||
    typeof v.cancelRequested !== "boolean" ||
    typeof v.supportsCancel !== "boolean" ||
    !["json", "suppressed-for-secret-inputs"].includes(
      String(v.resultVisibility),
    )
  ) {
    throw new AstronError("INVALID_EXECUTION_RESPONSE", true);
  }
  if (
    expected &&
    Object.entries(expected).some(
      ([k, value]) => value !== undefined && v[k] !== value,
    )
  ) {
    throw new AstronError("EXECUTION_TARGET_MISMATCH", true);
  }
  return jsonObject(v) as Snapshot;
}

export function checkIntegration(value: unknown): Record<string, unknown> {
  const v = object(value);
  if (
    v.contractVersion !== 1 ||
    v.profileSchemaVersion !== 1 ||
    v.requiredClientProtocol !== 1 ||
    v.durableIdempotency !== true ||
    !Array.isArray(v.operations) ||
    ![
      "workflow_list",
      "workflow_get",
      "workflow_execute",
      "execution_get",
      "execution_cancel",
    ].every((op) => (v.operations as unknown[]).includes(op))
  ) {
    throw new AstronError("CONTRACT_UNSUPPORTED");
  }
  return v;
}

export function checkWorkflow(
  value: unknown,
  projectId: string,
  version: number,
): Record<string, unknown> {
  const v = object(value);
  if (v.projectId !== projectId || v.version !== version)
    throw new AstronError("VERSION_NOT_ALLOWED");
  const p = object(v.profile);
  if (
    p.schemaVersion !== 1 ||
    p.projectId !== projectId ||
    p.version !== version ||
    object(p.admission).allowed !== true ||
    typeof p.revision !== "string"
  ) {
    throw new AstronError("ADMISSION_DENIED");
  }
  if (p.capabilityClass === "json-data") {
    const capabilities = p.capabilities;
    const limitsValue = p.jsonLimits;
    if (
      !Array.isArray(capabilities) ||
      !capabilities.includes("json-data") ||
      !limitsValue ||
      typeof limitsValue !== "object" ||
      Array.isArray(limitsValue) ||
      Object.getPrototypeOf(limitsValue) !== Object.prototype
    ) {
      throw new AstronError("CAPABILITY_UNSUPPORTED");
    }
    const limits = limitsValue as Record<string, unknown>;
    if (
      limits.maxBytes !== JSON_LIMITS.maxBytes ||
      limits.maxDepth !== JSON_LIMITS.maxDepth ||
      limits.maxObjectProperties !== JSON_LIMITS.maxObjectProperties ||
      limits.maxArrayItems !== JSON_LIMITS.maxArrayItems ||
      limits.maxStringLength !== JSON_LIMITS.maxStringLength
    ) {
      throw new AstronError("CAPABILITY_UNSUPPORTED");
    }
  }
  return p;
}
