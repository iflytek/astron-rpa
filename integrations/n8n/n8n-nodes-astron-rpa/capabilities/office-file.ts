import { validateFileContract } from "./shared/file-contract";
import type { CapabilityProfile } from "./shared/types";

export { FILE_LIMITS, safeFileName } from "./shared/file-contract";

export function validateOfficeFileProfile(profile: CapabilityProfile): void {
  validateFileContract(profile);
}
