const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  initialState,
  stateFrom,
  step,
  hash,
} = require("../dist/execution/runner");
const {
  AstronError,
  checkWorkflow,
  JSON_LIMITS,
  jsonObject,
  snapshot,
} = require("../dist/mapping/contracts");
const { endpoint, McpConnection } = require("../dist/transport/mcp");

const id = "11111111-1111-4111-a111-111111111111";
const info = {
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
const request = (changes = {}) => ({
  args: {
    projectId: "p",
    version: 1,
    params: { count: 0, flag: false, items: [null, { v: "" }] },
    idempotencyKey: "business-1",
    profileRevision: "r1",
  },
  mode: "wait",
  waitSeconds: 10,
  pollSeconds: 1,
  requestTimeout: 3,
  fingerprint: "fp",
  keyHash: "key-hash",
  itemIndex: 0,
  inputKeys: ["private"],
  parentExecutionId: "n8n-1",
  ...changes,
});
const receipt = (status = "running", changes = {}) => ({
  executionId: id,
  projectId: "p",
  version: 1,
  status,
  terminal: ["succeeded", "failed", "cancelled", "timeout"].includes(status),
  result: null,
  error: null,
  supportsCancel: true,
  cancelRequested: false,
  resultVisibility: "json",
  ...changes,
});

test("response loss replays the original key/content, then resumes by ID only", async () => {
  const req = request();
  const sent = [];
  let lost = true;
  const client = {
    call: async (tool, args) => {
      if (tool === "astron_integration_get") return info;
      if (tool === "astron_workflow_execute") {
        sent.push(structuredClone(args));
        if (lost) {
          lost = false;
          throw new AstronError("TRANSPORT_UNCONFIRMED", true);
        }
        return receipt();
      }
      assert.equal(args.executionId, id);
      return receipt("succeeded", { result: [0, false, null] });
    },
  };
  let state = await step(initialState([req], 0), [req], client, () => 1);
  assert.equal(state.active.attempts, 1);
  assert.equal(state.active.snapshot, undefined);
  state = stateFrom(JSON.parse(JSON.stringify(state)), 1);
  await step(state, [req], client, () => 1001);
  assert.equal(state.active.snapshot.executionId, id);
  assert.deepEqual(sent, [req.args, req.args]);
  await step(state, [req], client, () => 2001);
  assert.equal(state.done, true);
  assert.deepEqual(state.results[0].result, [0, false, null]);
  assert.equal(sent.length, 2);
  assert.equal(JSON.stringify(state).includes("business-1"), false);
});
test("wait expiry preserves actual status and blocks later items even on continue", async () => {
  const requests = [request(), request({ itemIndex: 1 })];
  let starts = 0;
  const client = {
    call: async (tool) => {
      if (tool === "astron_integration_get") return info;
      starts++;
      return receipt();
    },
  };
  const state = await step(
    initialState(requests, 0),
    requests,
    client,
    () => 1,
    true,
  );
  await step(state, requests, client, () => 10001, true);
  assert.equal(starts, 1);
  assert.equal(state.results[0].executionId, id);
  assert.equal(state.results[0].status, "running");
  assert.equal(state.results[0].callerError.code, "WAIT_BUDGET_EXPIRED");
  assert.equal(
    state.results[1].callerError.code,
    "PREVIOUS_EXECUTION_UNRESOLVED",
  );
});
test("no start after a wait budget elapsed while n8n was down", async () => {
  let calls = 0;
  const req = request();
  const state = await step(
    initialState([req], 0),
    [req],
    {
      call: async () => {
        calls++;
      },
    },
    () => 11000,
  );
  assert.equal(calls, 0);
  assert.equal(state.results[0].callerError.code, "WAIT_BUDGET_EXPIRED");
});
test("two unconfirmed sends remain unknown; no new implicit key or later task", async () => {
  const requests = [request(), request({ itemIndex: 1 })];
  let sends = 0;
  const client = {
    call: async (tool) => {
      if (tool === "astron_integration_get") return info;
      sends++;
      throw new AstronError("TRANSPORT_UNCONFIRMED", true);
    },
  };
  let s = initialState(requests, 0);
  s = await step(s, requests, client, () => 1, true);
  s = await step(s, requests, client, () => 2, true);
  assert.equal(s.done, true);
  assert.equal(sends, 2);
  assert.equal(s.results[0].correlation.keyHash, "key-hash");
});
test("unconfirmed reads never cause a second dispatch", async () => {
  const req = request();
  let starts = 0;
  const client = {
    call: async (tool) => {
      if (tool === "astron_integration_get") return info;
      if (tool === "astron_workflow_execute") {
        starts++;
        return receipt();
      }
      throw new AstronError("TRANSPORT_UNCONFIRMED", true);
    },
  };
  const state = await step(initialState([req], 0), [req], client, () => 1);
  await step(state, [req], client, () => 2);
  await step(state, [req], client, () => 12000);
  assert.equal(starts, 1);
  assert.equal(state.results[0].executionId, id);
});
test("confirmed failure is not success and later item can proceed on continue", async () => {
  const requests = [request(), request({ itemIndex: 1 })];
  const client = {
    call: async (tool) =>
      tool === "astron_integration_get"
        ? info
        : receipt("failed", {
            error: { code: "CLIENT_BUSY", message: "Busy" },
          }),
  };
  const state = await step(
    initialState(requests, 0),
    requests,
    client,
    () => 1,
    true,
  );
  assert.equal(state.cursor, 1);
  assert.equal(state.done, false);
  assert.equal(state.results[0].callerError.code, "CLIENT_BUSY");
});
test("preparation errors cannot dispatch and can preserve later item processing", async () => {
  const requests = [
    request({ preparationError: "INVALID_ARGUMENTS" }),
    request({ itemIndex: 1 }),
  ];
  let calls = 0;
  const s = await step(
    initialState(requests, 0),
    requests,
    {
      call: async () => {
        calls++;
      },
    },
    () => 1,
    true,
  );
  assert.equal(calls, 0);
  assert.equal(s.cursor, 1);
  assert.equal(s.results[0].callerError.code, "INVALID_ARGUMENTS");
});
test("invalid context/identity/state and non-JSON parameters fail closed", () => {
  assert.throws(() => stateFrom({ format: 2 }, 1));
  assert.throws(() => snapshot(receipt(), { executionId: "other" }));
  assert.throws(() => snapshot(receipt("running", { terminal: true })));
  for (const value of [
    { x: NaN },
    { x: undefined },
    { x: new Date() },
    [1],
    "{broken",
  ])
    assert.throws(() => jsonObject(value));
  const cyclic = {};
  cyclic.self = cyclic;
  assert.throws(
    () => jsonObject(cyclic),
    (error) => error.code === "INVALID_ARGUMENTS",
  );
  assert.deepEqual(
    jsonObject({ zero: 0, false: false, value: null, arr: [] }),
    { zero: 0, false: false, value: null, arr: [] },
  );
  assert.equal(hash({ b: 2, a: 1 }), hash({ a: 1, b: 2 }));
});
test("JSON data limits reject oversized values while preserving JSON scalars", () => {
  assert.deepEqual(jsonObject({ zero: 0, false: false, value: null }), {
    zero: 0,
    false: false,
    value: null,
  });
  for (const value of [
    { values: Array.from({ length: JSON_LIMITS.maxArrayItems + 1 }, () => 0) },
    { value: "x".repeat(JSON_LIMITS.maxStringLength + 1) },
  ])
    assert.throws(
      () => jsonObject(value),
      (error) => error.code === "JSON_LIMIT_EXCEEDED",
    );
  const nested = {};
  let current = nested;
  for (let index = 0; index <= JSON_LIMITS.maxDepth; index++) {
    current.next = {};
    current = current.next;
  }
  assert.throws(
    () => jsonObject(nested),
    (error) => error.code === "JSON_LIMIT_EXCEEDED",
  );
});
test("json-data workflow profiles must advertise the same bounded contract", () => {
  const value = {
    projectId: "p",
    version: 1,
    profile: {
      projectId: "p",
      version: 1,
      schemaVersion: 1,
      admission: { allowed: true },
      revision: "r1",
      capabilityClass: "json-data",
      capabilities: ["json-data"],
      jsonLimits: { ...JSON_LIMITS },
    },
  };
  assert.equal(checkWorkflow(value, "p", 1).capabilityClass, "json-data");
  value.profile.jsonLimits.maxDepth++;
  assert.throws(
    () => checkWorkflow(value, "p", 1),
    (error) => error.code === "CAPABILITY_UNSUPPORTED",
  );
});
test("endpoint refuses URL secrets, ambiguous paths, HTTP, query and fragment", () => {
  assert.equal(
    endpoint("https://rpa.example.com/api/mcp").href,
    "https://rpa.example.com/api/mcp/",
  );
  for (const url of [
    "http://example.com/mcp/",
    "https://key@example.com/mcp/",
    "https://example.com/mcp/?key=x",
    "https://example.com//mcp/",
    "https://example.com/mcp/mcp/",
    "https://example.com/mcp/#x",
  ])
    assert.throws(() => endpoint(url));
});
test("real SDK handshake, tool discovery and safe error normalization", async () => {
  const requests = [];
  const fetcher = async (url, init) => {
    requests.push(init);
    assert.equal(init.redirect, "error");
    if (init.method === "GET") return new Response(null, { status: 405 });
    const body = JSON.parse(init.body);
    if (!("id" in body)) return new Response(null, { status: 202 });
    const result =
      body.method === "initialize"
        ? {
            protocolVersion: "2025-11-25",
            capabilities: { tools: {} },
            serverInfo: { name: "test", version: "1" },
          }
        : body.method === "tools/list"
          ? {
              tools: [
                {
                  name: "astron_integration_get",
                  inputSchema: { type: "object" },
                },
              ],
            }
          : {
              isError: true,
              structuredContent: {
                error: {
                  code: "INVALID_ARGUMENTS",
                  message: "synthetic-secret",
                },
              },
              content: [],
            };
    return new Response(
      JSON.stringify({ jsonrpc: "2.0", id: body.id, result }),
      { headers: { "content-type": "application/json" } },
    );
  };
  const c = new McpConnection(
    {
      endpoint: "https://rpa.example.com/mcp/",
      apiKey: "synthetic-key",
      protocol: "2025-11-25",
    },
    3000,
    fetcher,
  );
  try {
    await c.connect();
    assert.deepEqual(await c.listTools(), ["astron_integration_get"]);
    await assert.rejects(
      c.call("astron_integration_get", {}),
      (e) =>
        e.code === "INVALID_ARGUMENTS" &&
        !e.message.includes("synthetic-secret"),
    );
  } finally {
    await c.close();
  }
  assert(requests.length >= 3);
});
