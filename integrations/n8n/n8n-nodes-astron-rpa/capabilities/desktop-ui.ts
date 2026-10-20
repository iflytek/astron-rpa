import { AstronError, object } from "../mapping/contracts";
import { DESKTOP_OPERATIONS, OFFICE_FILE_OPERATIONS } from "./shared/catalog";
import { validateFileContract } from "./shared/file-contract";
import type { CapabilityProfile } from "./shared/types";

const fileOperations = new Set([
  "BrowserElement.screenshot",
  "BrowserElement.position_screenshot",
  "BrowserSoftware.screenshot",
  "BrowserSoftware.download_web_file",
  "BrowserSoftware.upload_web_file",
  "System.screen_shot",
  "WinEle.screenshot_element",
]);

export function validateDesktopProfile(profile: CapabilityProfile): void {
  const contract = object(profile.desktopContract);
  const resolution = object(contract.resolution);
  const operations = profile.componentOperations;
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
    profile.exclusiveTerminal !== true ||
    !["low", "medium"].includes(String(profile.risk)) ||
    !Array.isArray(profile.capabilities) ||
    !profile.capabilities.includes("desktop-ui") ||
    !Array.isArray(profile.allowedTransports) ||
    !profile.allowedTransports.length ||
    !profile.allowedTransports.every((v) => v === "mcp" || v === "rest") ||
    !Array.isArray(profile.sideEffects) ||
    !profile.sideEffects.includes("desktop-interaction") ||
    !profile.sideEffects.every((v) =>
      [
        "desktop-interaction",
        "workspace-files",
        "external-file-transfer",
      ].includes(v),
    ) ||
    !Array.isArray(operations) ||
    !operations.length ||
    new Set(operations).size !== operations.length ||
    !operations.some((op) => DESKTOP_OPERATIONS.has(op)) ||
    !operations.every(
      (op) =>
        DESKTOP_OPERATIONS.has(op) ||
        (profile.fileContract && OFFICE_FILE_OPERATIONS.has(op)),
    ) ||
    (operations.some((op) => op.startsWith("Dialog.")) &&
      profile.requiresHuman !== true) ||
    (!profile.fileContract &&
      (profile.fileInputs !== false ||
        profile.fileOutputs !== false ||
        operations.some((op) => fileOperations.has(op))))
  )
    throw new AstronError("DESKTOP_CONTRACT_INVALID");
  if (profile.fileContract) validateFileContract(profile, true);
}
