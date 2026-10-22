const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const {
  validateCapabilityProfile,
} = require("../dist/capabilities/shared/registry");
const { JSON_LIMITS } = require("../dist/mapping/contracts");
const { COMPONENT_COVERAGE } = require("../dist/capabilities/shared/catalog");
const {
  DENIED_RISK_OPERATIONS,
} = require("../dist/capabilities/ai-dynamic-risk");

const profile = {
  capabilityClass: "ai-dynamic-risk",
  capabilities: ["ai-dynamic-risk"],
  componentOperations: ["ChatAI.single_turn_chat"],
  allowedTransports: ["mcp", "rest"],
  risk: "medium",
  requiresGui: false,
  requiresHuman: false,
  exclusiveTerminal: true,
  sideEffects: ["external-service"],
  fileInputs: false,
  fileOutputs: false,
  outputSchema: { type: "object" },
  jsonLimits: JSON_LIMITS,
  riskContract: {
    version: 1,
    approvalMode: "admin-exact-request",
    automaticExecution: false,
  },
};

test("risk is a peer capability requiring an exact administrator approval contract", () => {
  assert.deepEqual(validateCapabilityProfile(profile), profile);
  for (const changes of [
    { risk: "low" },
    { requiresHuman: true },
    { requiresGui: true },
    { exclusiveTerminal: false },
    { fileInputs: true },
    { outputSchema: null },
    { jsonLimits: {} },
    { allowedTransports: [] },
    { riskContract: { ...profile.riskContract, automaticExecution: true } },
    { componentOperations: ["ComputerUse.run"] },
    { componentOperations: ["ChatAI.chat"] },
    { componentOperations: ["System.screen_unlock"] },
    { componentOperations: [] },
  ])
    assert.throws(() => validateCapabilityProfile({ ...profile, ...changes }));
});

test("risk inventory includes AI, code, writes and deliberate autonomous denials", () => {
  const operations = new Set(
    COMPONENT_COVERAGE.flatMap((c) => c.riskOperations || []),
  );
  for (const operation of [
    "SemanticAI.choose",
    "Smart.run_code",
    "Script.module",
    "BrowserScript.js_run",
    "Database.execute_sql",
    "Email.send_email",
    "Network.ftp_delete",
    "Enterprise.upload_to_sharefolder",
    "System.run_command",
    "ComputerUse.run",
  ])
    assert.ok(operations.has(operation), operation);
});

test("risk operation inventory agrees with the server and admits no denied operation", () => {
  const source = readFileSync(
    resolve(
      __dirname,
      "../../../../backend/openapi-service/app/schemas/ai_dynamic_risk.py",
    ),
    "utf8",
  ).split("RISK_OPERATIONS =")[0];
  const operations = new Set(
    [...source.matchAll(/"([A-Za-z]+\.[a-z_]+)"/g)].map((m) => m[1]),
  );
  assert.deepEqual(
    [
      ...new Set(COMPONENT_COVERAGE.flatMap((c) => c.riskOperations || [])),
    ].sort(),
    [...operations].sort(),
  );
  for (const operation of DENIED_RISK_OPERATIONS) {
    assert.ok(operations.has(operation));
    assert.throws(() =>
      validateCapabilityProfile({
        ...profile,
        componentOperations: [operation],
      }),
    );
  }
});
