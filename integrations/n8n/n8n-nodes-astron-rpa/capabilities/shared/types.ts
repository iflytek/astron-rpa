export const CAPABILITY_CLASSES = [
  "json-data",
  "browser-read",
  "service-http-read",
  "service-database-read",
  "service-mail-read",
  "service-openapi-read",
  "service-shared-read",
] as const;

export type CapabilityClass = (typeof CAPABILITY_CLASSES)[number];
export type TransportName = "mcp" | "rest";

export interface CapabilityProfile {
  capabilityClass?: CapabilityClass;
  capabilities?: unknown;
  componentOperations?: unknown;
  readContractVersion?: unknown;
  allowedTransports?: unknown;
  fileInputs?: unknown;
  fileOutputs?: unknown;
  requiresGui?: unknown;
  requiresHuman?: unknown;
  risk?: unknown;
  sideEffects?: unknown;
  executionType?: unknown;
  jsonLimits?: unknown;
}
