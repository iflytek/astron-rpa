const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const {
  validateCapabilityProfile,
} = require("../dist/capabilities/shared/registry");
const {
  DESKTOP_OPERATIONS,
  COMPONENT_COVERAGE,
} = require("../dist/capabilities/shared/catalog");
const base = {
  capabilityClass: "desktop-ui",
  capabilities: ["desktop-ui"],
  componentOperations: ["Window.exist"],
  allowedTransports: ["mcp", "rest"],
  fileInputs: false,
  fileOutputs: false,
  requiresGui: true,
  requiresHuman: false,
  exclusiveTerminal: true,
  risk: "medium",
  sideEffects: ["desktop-interaction"],
  desktopContract: {
    version: 1,
    resolution: { width: 1920, height: 1080 },
    programs: ["editor"],
    humanMode: "none",
  },
};
test("desktop is a peer capability with an explicit environment contract", () => {
  assert.deepEqual(validateCapabilityProfile(base), base);
  for (const change of [
    { requiresGui: false },
    { requiresHuman: true },
    { exclusiveTerminal: false },
    { risk: "high" },
    { sideEffects: [] },
    { allowedTransports: [] },
    { fileInputs: true },
    { componentOperations: ["Software.cmd"] },
    { componentOperations: ["Software.close"] },
    { componentOperations: ["BrowserSoftware.browser_close"] },
    { componentOperations: ["ComputerUse.run"] },
    { componentOperations: ["System.screen_shot"] },
    { componentOperations: ["Dialog.input_box"] },
  ])
    assert.throws(
      () => validateCapabilityProfile({ ...base, ...change }),
      /DESKTOP_CONTRACT_INVALID/,
    );
});
test("attended dialogs require the matching human contract", () => {
  const profile = {
    ...base,
    requiresHuman: true,
    componentOperations: ["Dialog.input_box"],
    desktopContract: { ...base.desktopContract, humanMode: "attended" },
  };
  assert.deepEqual(validateCapabilityProfile(profile), profile);
});
test("desktop screenshots reuse bounded file contracts without admitting file-only workflows", () => {
  const { FILE_LIMITS } = require("../dist/capabilities/shared/file-contract");
  const profile = {
    ...base,
    componentOperations: ["Window.top", "System.screen_shot"],
    fileOutputs: true,
    sideEffects: ["desktop-interaction", "workspace-files"],
    fileContract: {
      version: 1,
      limits: FILE_LIMITS,
      inputs: {},
      outputs: { target: "screen.png" },
    },
  };
  assert.deepEqual(validateCapabilityProfile(profile), profile);
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...profile,
        componentOperations: ["File.file_write"],
      }),
    /DESKTOP_CONTRACT_INVALID/,
  );
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...profile,
        fileContract: {
          ...profile.fileContract,
          outputs: { target: "../screen.png" },
        },
      }),
    /FILE_NAME_INVALID/,
  );
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...profile,
        sideEffects: ["desktop-interaction"],
      }),
    /FILE_CONTRACT_INVALID/,
  );
});
test("desktop catalog agrees with server inventory and existing component groups", () => {
  const server = readFileSync(
    resolve(
      __dirname,
      "../../../../backend/openapi-service/app/schemas/desktop_ui.py",
    ),
    "utf8",
  ).split("DESKTOP_OPERATIONS =")[0];
  const operations = new Set(
    [...server.matchAll(/"([A-Za-z]+\.[a-z_]+)"/g)].map((m) => m[1]),
  );
  assert.deepEqual([...DESKTOP_OPERATIONS].sort(), [...operations].sort());
  for (const entry of COMPONENT_COVERAGE.filter((e) => e.desktopOperations))
    assert(entry.groups.includes("desktop-ui"));
});
