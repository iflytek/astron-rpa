"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const { evaluateAudit } = require("./check-n8n-audit.cjs");

const NOW = Date.parse("2026-10-27T00:00:00Z");
function fixture() {
  const lock = {
    lockfileVersion: 3,
    packages: {
      "": { devDependencies: { "n8n-workflow": "2.36.4" } },
      "node_modules/zod": { version: "3.25.76", dev: true },
      "node_modules/@n8n/expression-runtime": { version: "0.27.1", dev: true },
      "node_modules/n8n-workflow": { version: "2.36.4", dev: true },
    },
  };
  const via = {
    zod: [
      {
        name: "zod",
        dependency: "zod",
        severity: "high",
        range: "<4.6.6",
        url: "https://github.com/advisories/GHSA-mrhx-c7xc-m3w5",
      },
    ],
    "@n8n/expression-runtime": ["zod"],
    "n8n-workflow": ["@n8n/expression-runtime", "zod"],
  };
  const report = {
    auditReportVersion: 2,
    vulnerabilities: Object.fromEntries(
      Object.entries(via).map(([name, chain]) => [
        name,
        {
          name,
          severity: "high",
          via: chain,
          nodes: [`node_modules/${name}`],
        },
      ]),
    ),
    metadata: {
      vulnerabilities: {
        info: 0,
        low: 0,
        moderate: 0,
        high: 3,
        critical: 0,
        total: 3,
      },
    },
  };
  return { lock, report };
}
function evaluate(report, lock, status = 1, now = NOW) {
  return evaluateAudit({ status, stdout: JSON.stringify(report) }, lock, now);
}

test("accepts a clean full audit even after the exception expires", () => {
  const { lock, report } = fixture();
  report.vulnerabilities = {};
  report.metadata.vulnerabilities.high = 0;
  report.metadata.vulnerabilities.total = 0;
  assert.equal(evaluate(report, lock, 0, Date.parse("2027-01-01")).deferred, 0);
});

test("only the reviewed synthetic development fixture receives an explicit deferral", () => {
  const { lock, report } = fixture();
  assert.equal(evaluate(report, lock).deferred, 3);
});

for (const [label, mutate] of [
  [
    "new affected package",
    (r) => {
      r.vulnerabilities.newPackage = {
        ...r.vulnerabilities.zod,
        name: "newPackage",
      };
      r.metadata.vulnerabilities.high++;
      r.metadata.vulnerabilities.total++;
    },
  ],
  [
    "new advisory on the same package",
    (r) => {
      r.vulnerabilities.zod.via[0].url += "-different";
    },
  ],
  [
    "additional advisory",
    (r) => {
      r.vulnerabilities.zod.via.push({ ...r.vulnerabilities.zod.via[0] });
    },
  ],
  [
    "production dependency path",
    (r) => {
      r.vulnerabilities.zod.nodes = [
        "node_modules/@modelcontextprotocol/sdk/node_modules/zod",
      ];
    },
  ],
  [
    "additional dependency path",
    (r) => {
      r.vulnerabilities.zod.nodes.push("node_modules/another/node_modules/zod");
    },
  ],
  [
    "new transitive chain",
    (r) => {
      r.vulnerabilities["n8n-workflow"].via = ["another", "zod"];
    },
  ],
  [
    "changed advisory range",
    (r) => {
      r.vulnerabilities.zod.via[0].range = "<5";
    },
  ],
  [
    "critical severity",
    (r) => {
      r.vulnerabilities.zod.severity = "critical";
      r.metadata.vulnerabilities.high--;
      r.metadata.vulnerabilities.critical++;
    },
  ],
  [
    "inconsistent metadata",
    (r) => {
      r.metadata.vulnerabilities.high = 0;
    },
  ],
  [
    "incomplete advisory chain",
    (r) => {
      delete r.vulnerabilities.zod;
      r.metadata.vulnerabilities.high--;
      r.metadata.vulnerabilities.total--;
    },
  ],
  [
    "registry error",
    (r) => {
      r.error = { code: "E503" };
    },
  ],
  [
    "unsupported audit format",
    (r) => {
      r.auditReportVersion = 3;
    },
  ],
  [
    "missing finding details",
    (r) => {
      r.vulnerabilities.zod = null;
    },
  ],
]) {
  test(`rejects ${label}`, () => {
    const { lock, report } = fixture();
    mutate(report);
    assert.throws(() => evaluate(report, lock));
  });
}

for (const name of ["zod", "@n8n/expression-runtime", "n8n-workflow"]) {
  test(`rejects version or production-scope changes to ${name}`, () => {
    for (const edit of [
      (l) => {
        l.packages[`node_modules/${name}`].version = "99.0.0";
      },
      (l) => {
        delete l.packages[`node_modules/${name}`].dev;
      },
      (l) => {
        l.packages[""].dependencies = { [name]: "*" };
      },
    ]) {
      const { lock, report } = fixture();
      edit(lock);
      assert.throws(() => evaluate(report, lock));
    }
  });
}

test("expires at the declared UTC boundary", () => {
  const { lock, report } = fixture();
  assert.equal(
    evaluate(report, lock, 1, Date.parse("2026-11-10T23:59:59.999Z")).deferred,
    3,
  );
  assert.throws(() =>
    evaluate(report, lock, 1, Date.parse("2026-11-11T00:00:00Z")),
  );
});

test("does not turn process, network, JSON or contradictory status errors into success", () => {
  const { lock, report } = fixture();
  for (const result of [
    { status: null, signal: "SIGTERM", stdout: JSON.stringify(report) },
    { status: 1, error: new Error("timeout"), stdout: JSON.stringify(report) },
    { status: 2, stdout: JSON.stringify(report) },
    { status: 0, stdout: JSON.stringify(report) },
    { status: 1, stdout: "connection reset" },
    { status: 1, stdout: "{}" },
  ])
    assert.throws(() => evaluateAudit(result, lock, NOW));
});

test("release commands keep their strict full audit and cannot use the CI exception", () => {
  const root = path.resolve(__dirname, "../..");
  const pkg = JSON.parse(
    readFileSync(
      path.join(root, "integrations/n8n/n8n-nodes-astron-rpa/package.json"),
      "utf8",
    ),
  );
  assert.match(
    pkg.scripts["release:check"],
    /&& npm audit --include=dev --audit-level=moderate$/,
  );
  const workflow = readFileSync(
    path.join(root, ".github/workflows/publish-n8n.yml"),
    "utf8",
  );
  assert.match(
    workflow,
    /run: npm audit --include=dev --audit-level=moderate --json/,
  );
  assert.doesNotMatch(workflow, /check-n8n-audit|continue-on-error/);
});
