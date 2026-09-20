import { AstronError, JSON_LIMITS } from "../mapping/contracts";
import type { CapabilityProfile } from "./shared/types";

export function validateJsonDataProfile(profile: CapabilityProfile): void {
  if (profile.capabilityClass !== "json-data") return;
  const limits = profile.jsonLimits;
  if (
    !Array.isArray(profile.capabilities) ||
    !profile.capabilities.includes("json-data") ||
    !limits ||
    typeof limits !== "object" ||
    Array.isArray(limits) ||
    Object.getPrototypeOf(limits) !== Object.prototype
  ) {
    throw new AstronError("CAPABILITY_UNSUPPORTED");
  }
  const value = limits as Record<string, unknown>;
  if (
    value.maxBytes !== JSON_LIMITS.maxBytes ||
    value.maxDepth !== JSON_LIMITS.maxDepth ||
    value.maxObjectProperties !== JSON_LIMITS.maxObjectProperties ||
    value.maxArrayItems !== JSON_LIMITS.maxArrayItems ||
    value.maxStringLength !== JSON_LIMITS.maxStringLength
  ) {
    throw new AstronError("CAPABILITY_UNSUPPORTED");
  }
}
