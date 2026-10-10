import { AstronError } from "../mapping/contracts";
import { COMPONENT_COVERAGE } from "./shared/catalog";
import type {
  CapabilityClass,
  CapabilityProfile,
  TransportName,
} from "./shared/types";

// Stage 4.2 is a peer of json-data, not a layer built on its validator.
const operationClass = new Map<string, CapabilityClass>();
const componentClass: Readonly<Record<string, CapabilityClass>> = {
  "astronverse-browser": "browser-read",
  "astronverse-database": "service-database-read",
  "astronverse-email": "service-mail-read",
  "astronverse-network": "service-http-read",
  "astronverse-enterprise": "service-shared-read",
};
for (const entry of COMPONENT_COVERAGE) {
  const capability = componentClass[entry.component];
  for (const operation of entry.serviceReadOperations ?? []) {
    const owner = operationClass.get(operation);
    if (owner !== undefined && owner !== capability) {
      throw new Error(
        `Duplicate service operation classification: ${operation}`,
      );
    }
    if (capability !== undefined) operationClass.set(operation, capability);
  }
}

export function validateBrowserServiceProfile(
  profile: CapabilityProfile,
): void {
  if (
    !Array.isArray(profile.capabilities) ||
    !profile.capabilities.includes(profile.capabilityClass) ||
    profile.readContractVersion !== 1 ||
    !Array.isArray(profile.sideEffects) ||
    profile.sideEffects.length !== 0 ||
    !Array.isArray(profile.componentOperations) ||
    profile.componentOperations.length === 0 ||
    !profile.componentOperations.every(
      (operation) => typeof operation === "string" && operation.length > 0,
    ) ||
    !Array.isArray(profile.allowedTransports) ||
    profile.allowedTransports.length === 0 ||
    !profile.allowedTransports.every(
      (transport): transport is TransportName =>
        transport === "mcp" || transport === "rest",
    ) ||
    profile.fileInputs !== false ||
    profile.fileOutputs !== false ||
    profile.requiresHuman !== false ||
    (profile.capabilityClass === "browser-read"
      ? profile.requiresGui !== true
      : profile.requiresGui !== false) ||
    profile.componentOperations.some(
      (operation) => operationClass.get(operation) !== profile.capabilityClass,
    )
  ) {
    throw new AstronError("CAPABILITY_DECLARATION_INVALID");
  }
}
