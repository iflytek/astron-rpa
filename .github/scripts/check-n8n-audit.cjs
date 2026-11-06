"use strict";

// Regression CI only. Local release:check and publish-n8n retain strict audits.
// No compatible Zod 3 fix is published; a Zod 4 override changes n8n's schema
// semantics. Revisit this finite synthetic-test exception by 2026-11-10.
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const ADVISORY = "https://github.com/advisories/GHSA-mrhx-c7xc-m3w5";
const EXPIRES = "2026-11-11T00:00:00.000Z";
const FIXTURE = {
  zod: { version: "3.25.76", via: [ADVISORY] },
  "@n8n/expression-runtime": { version: "0.27.1", via: ["zod"] },
  "n8n-workflow": {
    version: "2.36.4",
    via: ["@n8n/expression-runtime", "zod"],
  },
};

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function object(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function evaluateAudit(result, lock, now = Date.now()) {
  requireCondition(
    !result.error && !result.signal && [0, 1].includes(result.status),
    "npm audit did not complete successfully",
  );
  let report;
  try {
    report = JSON.parse(result.stdout);
  } catch {
    throw new Error("npm audit returned invalid JSON");
  }
  requireCondition(
    report.auditReportVersion === 2 &&
      !report.error &&
      object(report.vulnerabilities) &&
      object(report.metadata?.vulnerabilities),
    "npm audit returned an error or unsupported report",
  );
  const counts = { info: 0, low: 0, moderate: 0, high: 0, critical: 0 };
  const entries = Object.entries(report.vulnerabilities);
  for (const [, finding] of entries) {
    requireCondition(
      object(finding) && Object.hasOwn(counts, finding.severity),
      "npm audit returned an invalid finding",
    );
    counts[finding.severity]++;
  }
  requireCondition(
    Object.entries({ ...counts, total: entries.length }).every(
      ([key, value]) => report.metadata.vulnerabilities[key] === value,
    ) &&
      result.status ===
        (counts.moderate + counts.high + counts.critical > 0 ? 1 : 0),
    "npm audit counts or exit status do not match its findings",
  );
  if (entries.length === 0) return { deferred: 0 };

  requireCondition(
    Number.isFinite(now) && now < Date.parse(EXPIRES),
    "The regression-only dependency exception has expired; review upstream fixes",
  );
  requireCondition(
    JSON.stringify(entries.map(([name]) => name).sort()) ===
      JSON.stringify(Object.keys(FIXTURE).sort()),
    "The reviewed set of affected packages has changed",
  );
  requireCondition(
    lock?.lockfileVersion === 3 &&
      lock.packages?.[""]?.devDependencies?.["n8n-workflow"] === "2.36.4",
    "The reviewed development fixture has changed",
  );
  for (const [name, reviewed] of Object.entries(FIXTURE)) {
    const installed = lock.packages[`node_modules/${name}`];
    requireCondition(
      installed?.dev === true &&
        installed.version === reviewed.version &&
        !Object.hasOwn(lock.packages[""].dependencies ?? {}, name) &&
        !Object.hasOwn(lock.packages[""].optionalDependencies ?? {}, name),
      "An exception dependency changed version or is no longer development-only",
    );
  }
  for (const [name, finding] of entries) {
    const reviewed = Object.hasOwn(FIXTURE, name) ? FIXTURE[name] : undefined;
    requireCondition(
      reviewed &&
        finding.name === name &&
        finding.severity === "high" &&
        Array.isArray(finding.nodes) &&
        finding.nodes.length === 1 &&
        finding.nodes[0] === `node_modules/${name}` &&
        Array.isArray(finding.via) &&
        finding.via.length === reviewed.via.length,
      "Unreviewed vulnerability, severity or dependency path; inspect the audit report",
    );
    const via = finding.via.map((item) => {
      if (typeof item === "string") return item;
      requireCondition(
        object(item) &&
          name === "zod" &&
          item.name === "zod" &&
          item.dependency === "zod" &&
          item.severity === "high" &&
          item.range === "<4.6.6",
        "The reviewed advisory has changed",
      );
      return item.url;
    });
    requireCondition(
      JSON.stringify(via.sort()) === JSON.stringify([...reviewed.via].sort()),
      "A new advisory or dependency chain is not covered by the exception",
    );
  }
  return { deferred: entries.length, expires: EXPIRES, advisory: ADVISORY };
}

function main() {
  const reportFile = process.argv[2];
  requireCondition(Boolean(reportFile), "Supply an external audit report path");
  const cwd = path.resolve(
    __dirname,
    "../../integrations/n8n/n8n-nodes-astron-rpa",
  );
  // The Windows command is a fixed literal; report paths never enter a shell.
  const windows = process.platform === "win32";
  const result = spawnSync(
    windows ? process.env.ComSpec || "cmd.exe" : "npm",
    windows
      ? [
          "/d",
          "/s",
          "/c",
          "npm audit --include=dev --audit-level=moderate --json",
        ]
      : ["audit", "--include=dev", "--audit-level=moderate", "--json"],
    {
      cwd,
      encoding: "utf8",
      timeout: 120000,
      maxBuffer: 10 * 1024 * 1024,
    },
  );
  fs.writeFileSync(reportFile, result.stdout || "", "utf8");
  const lock = JSON.parse(
    fs.readFileSync(path.join(cwd, "package-lock.json"), "utf8"),
  );
  const decision = evaluateAudit(result, lock);
  if (decision.deferred) {
    console.warn(
      `::warning::GHSA-mrhx-c7xc-m3w5: ${decision.deferred} known development-only findings retained. Regression-only exception expires ${EXPIRES}; release audits remain blocking.`,
    );
  } else {
    console.log("Full dependency audit: no findings.");
  }
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`Dependency audit failed: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = { evaluateAudit };
