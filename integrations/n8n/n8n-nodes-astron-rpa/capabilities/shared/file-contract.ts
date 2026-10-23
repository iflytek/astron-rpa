import { AstronError, object } from "../../mapping/contracts";
import { OFFICE_FILE_OPERATIONS, DESKTOP_OPERATIONS } from "./catalog";
import type { CapabilityProfile } from "./types";

export const FILE_LIMITS = {
  maxFileBytes: 10 * 1024 * 1024,
  maxFiles: 8,
  retentionSeconds: 86400,
} as const;

export function safeFileName(value: unknown): string {
  if (
    typeof value !== "string" ||
    value.length < 1 ||
    value.length > 160 ||
    /[\\/:<>"|?*\x00-\x1f\x7f]/.test(value) ||
    /[. ]$/.test(value) ||
    /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(value)
  )
    throw new AstronError("FILE_NAME_INVALID");
  return value;
}

export function validateFileBindings(profile: CapabilityProfile): void {
  const contract = object(profile.fileContract);
  const inputs = object(contract.inputs);
  const outputs = object(contract.outputs);
  const limits = object(contract.limits);
  const operations = profile.componentOperations;
  if (
    contract.version !== 1 ||
    Object.keys(contract).sort().join() !== "inputs,limits,outputs,version" ||
    !Object.entries(FILE_LIMITS).every(
      ([key, value]) => limits[key] === value,
    ) ||
    !Array.isArray(operations) ||
    !operations.length ||
    !Array.isArray(profile.allowedTransports) ||
    !profile.allowedTransports.length ||
    !profile.allowedTransports.every((v) => v === "mcp" || v === "rest") ||
    profile.fileInputs !== Object.keys(inputs).length > 0 ||
    profile.fileOutputs !== Object.keys(outputs).length > 0 ||
    profile.exclusiveTerminal !== true ||
    !Array.isArray(profile.sideEffects) ||
    (Object.keys(outputs).length > 0 &&
      !profile.sideEffects.includes("workspace-files")) ||
    Object.keys(inputs).length + Object.keys(outputs).length < 1 ||
    Object.keys(inputs).length + Object.keys(outputs).length >
      FILE_LIMITS.maxFiles ||
    Object.keys(inputs).some((key) => Object.hasOwn(outputs, key)) ||
    [...Object.keys(inputs), ...Object.keys(outputs)].some(
      (key) => !/^[A-Za-z_][A-Za-z0-9_]*$/.test(key),
    )
  )
    throw new AstronError("FILE_CONTRACT_INVALID");
  for (const extensions of Object.values(inputs)) {
    if (
      !Array.isArray(extensions) ||
      !extensions.length ||
      !extensions.every(
        (v) => typeof v === "string" && /^\.[a-z0-9]{1,11}$/i.test(v),
      )
    )
      throw new AstronError("FILE_CONTRACT_INVALID");
  }
  Object.values(outputs).forEach(safeFileName);
  if (
    operations.some(
      (op) =>
        /^(Network\.|Enterprise\.|OpenApi\.|Email\.)/.test(op) ||
        [
          "BrowserSoftware.upload_web_file",
          "BrowserSoftware.download_web_file",
        ].includes(op),
    ) &&
    !profile.sideEffects.includes("external-file-transfer")
  )
    throw new AstronError("FILE_CONTRACT_INVALID");
  if (
    new Set(Object.values(outputs).map((name) => String(name).toLowerCase()))
      .size !== Object.keys(outputs).length
  )
    throw new AstronError("FILE_CONTRACT_INVALID");
}

export function validateFileContract(
  profile: CapabilityProfile,
  desktop = false,
): void {
  validateFileBindings(profile);
  const operations = profile.componentOperations as string[];
  if (
    !Array.isArray(profile.capabilities) ||
    !profile.capabilities.includes(desktop ? "desktop-ui" : "office-file") ||
    !operations.every(
      (op) =>
        OFFICE_FILE_OPERATIONS.has(op) ||
        (desktop && DESKTOP_OPERATIONS.has(op)),
    ) ||
    (!desktop && profile.requiresHuman !== false) ||
    !["low", "medium"].includes(String(profile.risk)) ||
    !(profile.sideEffects as string[]).every((v) =>
      [
        "workspace-files",
        "external-file-transfer",
        ...(desktop ? ["desktop-interaction"] : []),
      ].includes(v),
    ) ||
    profile.requiresGui !==
      (desktop || operations.some((op) => /^(Excel\.|Docx\.|Browser)/.test(op)))
  )
    throw new AstronError("FILE_CONTRACT_INVALID");
}
