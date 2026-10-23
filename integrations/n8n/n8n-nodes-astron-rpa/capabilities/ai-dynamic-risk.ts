import { AstronError, JSON_LIMITS, object } from "../mapping/contracts";
import { validateFileBindings } from "./shared/file-contract";
import { validateDesktopEnvironment } from "./shared/desktop-contract";
import type { CapabilityProfile } from "./shared/types";
import {
  COMPONENT_COVERAGE,
  DESKTOP_OPERATIONS,
  OFFICE_FILE_OPERATIONS,
} from "./shared/catalog";

const riskOperations = new Set(
  COMPONENT_COVERAGE.flatMap((c) => c.riskOperations || []),
);
const readOperations = new Set(
  COMPONENT_COVERAGE.flatMap((c) => c.serviceReadOperations || []),
);
const fileRequiredOperations = new Set(
  [...OFFICE_FILE_OPERATIONS].filter((op) => !readOperations.has(op)),
);

export const DENIED_RISK_OPERATIONS = new Set([
  "ChatAI.chat",
  "ChatAI.knowledge_chat",
  "System.screen_unlock",
  "ComputerUse.run",
  "ComputerUse.custom_action_screen",
  "ComputerUse.extract_data",
  "ComputerUse.fill_form",
  "ComputerUse.process_captcha",
  "VerifyCode.picture_code",
  "VerifyCode.slider_code",
  "VerifyCode.click_code",
]);

export function validateRiskProfile(profile: CapabilityProfile): void {
  const contract = object(profile.riskContract);
  const limits = object(profile.jsonLimits);
  const operations = profile.componentOperations;
  if (
    Object.keys(contract).sort().join() !==
      "approvalMode,automaticExecution,version" ||
    contract.version !== 1 ||
    contract.approvalMode !== "admin-exact-request" ||
    contract.automaticExecution !== false ||
    !["medium", "high"].includes(String(profile.risk)) ||
    profile.requiresHuman !== false ||
    profile.exclusiveTerminal !== true ||
    !Object.keys(object(profile.outputSchema)).length ||
    !Object.entries(JSON_LIMITS).every(
      ([key, value]) => limits[key] === value,
    ) ||
    !Array.isArray(profile.capabilities) ||
    !profile.capabilities.includes("ai-dynamic-risk") ||
    !Array.isArray(profile.allowedTransports) ||
    !profile.allowedTransports.length ||
    !profile.allowedTransports.every((v) => v === "mcp" || v === "rest") ||
    !Array.isArray(operations) ||
    !operations.length ||
    operations.length > 256 ||
    new Set(operations).size !== operations.length ||
    !operations.some((op) => riskOperations.has(op)) ||
    !operations.every(
      (op) =>
        typeof op === "string" &&
        /^[A-Za-z][A-Za-z0-9_]*\.[a-z][a-z0-9_]*$/.test(op) &&
        !DENIED_RISK_OPERATIONS.has(op),
    ) ||
    operations.some((op) => op.startsWith("Dialog.")) ||
    !Array.isArray(profile.sideEffects) ||
    !profile.sideEffects.every((v) =>
      [
        "external-service",
        "external-write",
        "dynamic-code",
        "desktop-interaction",
        "workspace-files",
        "external-file-transfer",
      ].includes(v),
    ) ||
    (!profile.fileContract &&
      (profile.fileInputs !== false || profile.fileOutputs !== false)) ||
    profile.requiresGui !== Boolean(profile.desktopContract) ||
    (operations.some(
      (op) =>
        DESKTOP_OPERATIONS.has(op) || /^(Excel\.|Docx\.|Browser)/.test(op),
    ) &&
      !profile.desktopContract) ||
    (operations.some(
      (op) =>
        fileRequiredOperations.has(op) ||
        /^(Excel\.|Docx\.|File\.|Folder\.|Compress\.)/.test(op) ||
        [
          "System.screen_shot",
          "WinEle.screenshot_element",
          "BrowserElement.screenshot",
          "BrowserElement.position_screenshot",
          "BrowserSoftware.screenshot",
          "BrowserSoftware.download_web_file",
          "BrowserSoftware.upload_web_file",
        ].includes(op),
    ) &&
      !profile.fileContract)
  )
    throw new AstronError("RISK_CONTRACT_INVALID");
  if (profile.fileContract) validateFileBindings(profile);
  if (profile.desktopContract) validateDesktopEnvironment(profile);
}
