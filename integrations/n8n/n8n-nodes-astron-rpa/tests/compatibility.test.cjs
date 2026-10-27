const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  checkIntegration,
  checkWorkflow,
} = require("../dist/mapping/contracts");

const contract = {
  contractVersion: 1,
  profileSchemaVersion: 1,
  requiredClientProtocol: 1,
  durableIdempotency: true,
  operations: [
    "workflow_list",
    "workflow_get",
    "workflow_execute",
    "execution_get",
    "execution_cancel",
  ],
};

test("business contract versions are checked independently of display/server version", () => {
  for (const field of [
    "contractVersion",
    "profileSchemaVersion",
    "requiredClientProtocol",
  ])
    for (const version of [0, 2, "1", null])
      assert.throws(
        () => checkIntegration({ ...contract, [field]: version }),
        (e) => e.code === "CONTRACT_UNSUPPORTED",
      );
  assert.throws(
    () => checkIntegration({ ...contract, operations: ["workflow_list"] }),
    (e) => e.code === "CONTRACT_UNSUPPORTED",
  );
  assert.equal(
    checkIntegration({ ...contract, serviceVersion: "display-only" })
      .serviceVersion,
    "display-only",
  );
});

test("workflow rename preserves immutable identity while version/profile changes fail closed", () => {
  const profile = {
    projectId: "stable-project",
    version: 1,
    schemaVersion: 1,
    admission: { allowed: true },
    revision: "review-1",
  };
  for (const name of ["before rename", "after rename"])
    assert.equal(
      checkWorkflow(
        { projectId: "stable-project", version: 1, name, profile },
        "stable-project",
        1,
      ),
      profile,
    );
  assert.throws(
    () =>
      checkWorkflow(
        { projectId: "stable-project", version: 2, profile },
        "stable-project",
        1,
      ),
    (e) => e.code === "VERSION_NOT_ALLOWED",
  );
  assert.throws(
    () =>
      checkWorkflow(
        {
          projectId: "stable-project",
          version: 1,
          profile: { ...profile, schemaVersion: 2 },
        },
        "stable-project",
        1,
      ),
    (e) => e.code === "ADMISSION_DENIED",
  );
});
