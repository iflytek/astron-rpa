import { AstronError, object } from "../../mapping/contracts";
import type { CapabilityProfile } from "./types";

export function validateDesktopEnvironment(profile: CapabilityProfile): void {
  const contract = object(profile.desktopContract);
  const resolution = object(contract.resolution);
  if (
    contract.version !== 1 ||
    Object.keys(contract).sort().join() !==
      "humanMode,programs,resolution,version" ||
    Object.keys(resolution).sort().join() !== "height,width" ||
    !Object.values(resolution).every(
      (v) => Number.isInteger(v) && Number(v) >= 320 && Number(v) <= 16384,
    ) ||
    !Array.isArray(contract.programs) ||
    !contract.programs.length ||
    contract.programs.length > 16 ||
    !contract.programs.every(
      (v) => typeof v === "string" && v.length > 0 && v.length <= 64,
    ) ||
    new Set(contract.programs).size !== contract.programs.length ||
    !["none", "attended"].includes(String(contract.humanMode)) ||
    profile.requiresHuman !== (contract.humanMode === "attended") ||
    profile.requiresGui !== true ||
    profile.exclusiveTerminal !== true
  )
    throw new AstronError("DESKTOP_CONTRACT_INVALID");
}
