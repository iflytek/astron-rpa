const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readdirSync } = require("node:fs");
const { resolve } = require("node:path");
const { JSON_LIMITS } = require("../dist/mapping/contracts");
const {
  validateCapabilityProfile,
} = require("../dist/capabilities/shared/registry");
const {
  CAPABILITY_GROUPS,
  COMPONENT_COVERAGE,
  BROWSER_SERVICE_COMPONENTS,
} = require("../dist/capabilities/shared/catalog");

const base = {
  capabilities: ["service-http-read"],
  capabilityClass: "service-http-read",
  componentOperations: ["Network.http_request"],
  allowedTransports: ["mcp", "rest"],
  fileInputs: false,
  fileOutputs: false,
  requiresGui: false,
  requiresHuman: false,
};

test("service capability profiles preserve operation and transport declarations", () => {
  assert.deepEqual(validateCapabilityProfile(base), base);
});

test("peer capability groups validate independently without another group's fields", () => {
  const json = {
    capabilityClass: "json-data",
    capabilities: ["json-data"],
    jsonLimits: { ...JSON_LIMITS },
  };
  assert.deepEqual(validateCapabilityProfile(json), json);
  assert.throws(
    () => validateCapabilityProfile({ ...json, capabilities: [] }),
    /CAPABILITY_UNSUPPORTED/,
  );
  for (const [capabilityClass, operation] of [
    ["browser-read", "BrowserSoftware.get_current_url"],
    ["service-http-read", "Network.http_request"],
    ["service-database-read", "Database.query_sql"],
    ["service-mail-read", "Email.receive_email"],
    ["service-shared-read", "Enterprise.get_shared_variable"],
  ]) {
    const profile = {
      ...base,
      capabilityClass,
      capabilities: [capabilityClass],
      componentOperations: [operation],
      requiresGui: capabilityClass === "browser-read",
    };
    assert.deepEqual(validateCapabilityProfile(profile), profile);
  }
});

test("service capability profiles reject missing operation declarations", () => {
  assert.throws(
    () => validateCapabilityProfile({ ...base, componentOperations: [] }),
    /CAPABILITY_DECLARATION_INVALID/,
  );
});

test("browser-read requires a GUI-backed browser declaration", () => {
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...base,
        capabilities: ["browser-read"],
        capabilityClass: "browser-read",
        requiresGui: false,
      }),
    /CAPABILITY_DECLARATION_INVALID/,
  );
});

test("service declarations accept only operation-level reads from the catalog", () => {
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...base,
        componentOperations: ["Network.ftp_upload"],
      }),
    /CAPABILITY_DECLARATION_INVALID/,
  );
  assert.throws(
    () =>
      validateCapabilityProfile({
        ...base,
        capabilities: ["service-openapi-read"],
        capabilityClass: "service-openapi-read",
        componentOperations: ["OpenApi.common_ocr"],
      }),
    /CAPABILITY_DECLARATION_INVALID/,
  );
});

test("the operation inventory covers every Engine component directory", () => {
  const components = readdirSync(
    resolve(__dirname, "../../../../engine/components"),
    {
      withFileTypes: true,
    },
  )
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
  assert.deepEqual(
    COMPONENT_COVERAGE.map((entry) => entry.component).sort(),
    components,
  );
  for (const entry of COMPONENT_COVERAGE) {
    assert(entry.groups.length > 0);
    assert(
      entry.groups.every((group) => Object.hasOwn(CAPABILITY_GROUPS, group)),
    );
  }
  assert.deepEqual(
    BROWSER_SERVICE_COMPONENTS.map((entry) => entry.component),
    [
      "astronverse-browser",
      "astronverse-database",
      "astronverse-email",
      "astronverse-enterprise",
      "astronverse-network",
    ],
  );
});

test("json-data profiles enforce the same bounded contract", () => {
  const profile = {
    capabilityClass: "json-data",
    capabilities: ["json-data"],
    jsonLimits: { ...JSON_LIMITS },
  };
  assert.equal(validateCapabilityProfile(profile).capabilityClass, "json-data");
  profile.jsonLimits.maxDepth++;
  assert.throws(
    () => validateCapabilityProfile(profile),
    (error) => error.code === "CAPABILITY_UNSUPPORTED",
  );
});
