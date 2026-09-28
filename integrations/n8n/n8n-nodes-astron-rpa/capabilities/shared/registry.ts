import { AstronError, object } from "../../mapping/contracts";
import { validateBrowserServiceProfile } from "../browser-service";
import { validateJsonDataProfile } from "../json-data";
import {
  CAPABILITY_CLASSES,
  type CapabilityClass,
  type CapabilityProfile,
  type TransportName,
} from "./types";

const knownClasses = new Set<string>(CAPABILITY_CLASSES);
// Every class dispatches directly to its own peer capability module.
// Registry entries express support, not implementation order or inheritance.
const validators: Record<
  CapabilityClass,
  (profile: CapabilityProfile) => void
> = {
  "json-data": validateJsonDataProfile,
  "browser-read": validateBrowserServiceProfile,
  "service-http-read": validateBrowserServiceProfile,
  "service-database-read": validateBrowserServiceProfile,
  "service-mail-read": validateBrowserServiceProfile,
  "service-openapi-read": validateBrowserServiceProfile,
  "service-shared-read": validateBrowserServiceProfile,
};

export function validateCapabilityProfile(value: unknown): CapabilityProfile {
  const profile = object(value) as CapabilityProfile;
  if (profile.capabilityClass === undefined) return profile;
  const capability = capabilityClass(profile.capabilityClass);
  if (capability === undefined) throw new AstronError("CAPABILITY_UNSUPPORTED");
  validators[capability](profile);
  return profile;
}

export function capabilityClass(value: unknown): CapabilityClass | undefined {
  if (typeof value !== "string" || !knownClasses.has(value)) return undefined;
  return value as CapabilityClass;
}

export function allowsTransport(
  profile: CapabilityProfile,
  transport: TransportName,
): boolean {
  if (!Array.isArray(profile.allowedTransports)) return transport === "mcp";
  return profile.allowedTransports.includes(transport);
}
