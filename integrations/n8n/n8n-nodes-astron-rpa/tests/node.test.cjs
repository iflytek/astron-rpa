const { test } = require("node:test");
const assert = require("node:assert/strict");
const { AstronRpa } = require("../dist/nodes/AstronRpa/AstronRpa.node");
const { runnerWorkflow } = require("../dist/execution/workflow");
const transport = require("../dist/transport/mcp");
const { AstronError } = require("../dist/mapping/contracts");

test("prepared keys isolate execution/run/item and retries cannot reevaluate changed requests", async () => {
  const saved = transport.withMcp;
  transport.withMcp = async (_connection, _timeout, action) =>
    action({
      call: async (name) =>
        name === "astron_integration_get"
          ? {
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
            }
          : {
              projectId: "p",
              version: 1,
              profile: {
                projectId: "p",
                version: 1,
                schemaVersion: 1,
                admission: { allowed: true },
                revision: "frozen",
              },
            },
    });
  const state = {};
  let run = 0,
    execution = "parent-1",
    params = { value: 0 };
  let prepared;
  const context = {
    getNodeParameter: (name, _index, fallback) =>
      ({ operation: "execute", projectId: "p", version: 1, params })[name] ??
      fallback,
    getInputData: () => [{ json: {} }, { json: {} }],
    getCredentials: async () => ({}),
    getInstanceId: () => "instance",
    getExecutionId: () => execution,
    getNode: () => ({ id: "node", name: "AstronRPA" }),
    getWorkflowDataProxy: () => ({ $runIndex: run }),
    getContext: () => state,
    getWorkflow: () => ({ id: "workflow" }),
    getMode: () => "manual",
    continueOnFail: () => false,
    setMetadata: () => {},
    executeWorkflow: async (_workflow, input) => {
      prepared = input[0].json.requests;
      return { executionId: "child", data: [[]] };
    },
  };
  try {
    const node = new AstronRpa();
    await node.execute.call(context);
    const keys = prepared.map((r) => r.args.idempotencyKey);
    assert.notEqual(keys[0], keys[1]);
    await node.execute.call(context);
    assert.deepEqual(
      prepared.map((r) => r.args.idempotencyKey),
      keys,
    );
    params = { value: 1 };
    await assert.rejects(
      node.execute.call(context),
      /REQUEST_CHANGED_ON_RETRY/,
    );
    params = { value: 0 };
    run = 1;
    await node.execute.call(context);
    assert(!keys.includes(prepared[0].args.idempotencyKey));
    run = 0;
    execution = "parent-2";
    for (const key of Object.keys(state)) delete state[key];
    await node.execute.call(context);
    assert(!keys.includes(prepared[0].args.idempotencyKey));
    assert.equal(prepared[0].args.profileRevision, "frozen");
  } finally {
    transport.withMcp = saved;
  }
});

test("query/cancel reject arbitrary IDs without reflecting input; connection failures retain valid IDs", async () => {
  const saved = transport.withMcp;
  let calls = 0;
  transport.withMcp = async () => {
    calls++;
    throw new AstronError("TRANSPORT_UNCONFIRMED", true);
  };
  try {
    for (const operation of ["getExecution", "cancelExecution"]) {
      for (const valid of [false, true]) {
        const executionId = valid
          ? "11111111-1111-4111-a111-111111111111"
          : "synthetic-private-input";
        const context = {
          getNodeParameter: (name, _index, fallback) =>
            ({ operation, executionId })[name] ?? fallback,
          getInputData: () => [
            { json: { private: "synthetic-private-input" } },
          ],
          getCredentials: async () => ({}),
          getNode: () => ({ name: "AstronRPA" }),
          continueOnFail: () => true,
        };
        const [[result]] = await new AstronRpa().execute.call(context);
        const envelope = JSON.parse(result.error.message);
        assert.equal(
          envelope.code,
          valid ? "TRANSPORT_UNCONFIRMED" : "INVALID_EXECUTION_ID",
        );
        assert.equal(envelope.executionId, valid ? executionId : undefined);
        assert(!JSON.stringify(result).includes("synthetic-private-input"));
      }
    }
    assert.equal(calls, 2);
  } finally {
    transport.withMcp = saved;
  }
});

test("native n8n error-json rewriting still preserves execution ID and paired item", async () => {
  const executionId = "11111111-1111-4111-a111-111111111111";
  const requests = [{ inputKeys: ["private"], itemIndex: 0 }];
  const value = {
    executionId,
    projectId: "p",
    version: 1,
    status: "failed",
    terminal: true,
    result: null,
    callerError: { code: "EXECUTION_FAILED" },
    correlation: { keyHash: "hash" },
  };
  const ctx = {
    getNodeParameter: (name) =>
      ({ operation: "_result", _requests: requests, _continue: true })[name],
    getInputData: () => [
      {
        json: {
          format: 1,
          cursor: 1,
          active: { deadline: 10, attempts: 1 },
          results: [value],
          done: true,
          nextPoll: 0,
        },
      },
    ],
    getNode: () => ({ name: "AstronRPA" }),
  };
  const [[out]] = await new AstronRpa().execute.call(ctx);
  // Host workflow-execute replaces json whenever item.error is present.
  const persisted = {
    json: { error: out.error.message },
    pairedItem: out.pairedItem,
  };
  assert.equal(JSON.parse(persisted.json.error).executionId, executionId);
  assert.equal(JSON.parse(persisted.json.error).status, "failed");
  assert.deepEqual(persisted.pairedItem, { item: 0 });
  assert(!persisted.json.error.includes("private"));
});
test("stop errors retain the same safe snapshot", async () => {
  const value = {
    executionId: "11111111-1111-4111-a111-111111111111",
    callerError: { code: "WAIT_BUDGET_EXPIRED" },
  };
  const ctx = {
    getNodeParameter: (name) =>
      ({ operation: "_result", _requests: [{}], _continue: false })[name],
    getInputData: () => [
      {
        json: {
          format: 1,
          cursor: 1,
          active: { deadline: 1, attempts: 1 },
          results: [value],
          done: true,
          nextPoll: 0,
        },
      },
    ],
    getNode: () => ({ name: "AstronRPA" }),
  };
  await assert.rejects(
    new AstronRpa().execute.call(ctx),
    (e) => JSON.parse(e.message).executionId === value.executionId,
  );
});
test("resume callback ignores supplied result and preserves persisted state", async () => {
  const state = {
    format: 1,
    cursor: 0,
    active: { deadline: 10, attempts: 0 },
    results: [],
    done: false,
    nextPoll: 1,
  };
  const context = {
    getNodeParameter: (name) =>
      ({ operation: "_pause", _requests: [{}], _resumeState: state })[name],
    getBodyData: () => {
      throw new Error("callback must not read body");
    },
  };
  const response = await new AstronRpa().webhook.call(context);
  assert.deepEqual(response.workflowData[0][0].json, state);
});
test("inline workflow uses credential references and checkpoint before observation", () => {
  const parent = {
    name: "Astron",
    type: "n8n-nodes-astron-rpa.astronRpa",
    typeVersion: 1,
    credentials: { astronRpaApi: { id: "credential-reference", name: "test" } },
  };
  const workflow = runnerWorkflow(parent, true);
  assert.equal(workflow.connections.State.main[0][0].node, "Checkpoint");
  assert.equal(workflow.connections.Checkpoint.main[0][0].node, "Observe");
  assert.equal(
    workflow.nodes.find((n) => n.name === "Observe").credentials.astronRpaApi
      .id,
    "credential-reference",
  );
  assert(!JSON.stringify(workflow).includes("apiKey"));
});
