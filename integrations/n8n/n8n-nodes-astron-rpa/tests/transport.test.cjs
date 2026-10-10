const { test } = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const { once } = require("node:events");
const { McpConnection } = require("../dist/transport/mcp");
const { RestConnection } = require("../dist/transport/rest");

const connection = {
  endpoint: "https://rpa.example.com/mcp/",
  apiKey: "synthetic-test-key",
  protocol: "2025-11-25",
};

async function server(t, handler) {
  const instance = http.createServer(handler);
  instance.listen(0, "127.0.0.1");
  await once(instance, "listening");
  t.after(async () => {
    instance.closeAllConnections();
    await new Promise((resolve) => instance.close(resolve));
  });
  return `http://127.0.0.1:${instance.address().port}`;
}

// Only the injected test fetch maps the configured HTTPS endpoint to loopback.
// Production transport still requires HTTPS and uses normal certificate checks.
const loopbackFetch = (origin) => (url, init) => {
  assert.equal(String(url), connection.endpoint);
  return fetch(`${origin}/mcp/`, init);
};

test("real fetch refuses a cross-origin redirect before credentials can reach it", async (t) => {
  let destinationRequests = 0;
  const destination = await server(t, (_req, res) => {
    destinationRequests++;
    res.end("{}");
  });
  let sourceRequests = 0;
  const source = await server(t, (req, res) => {
    sourceRequests++;
    assert.equal(req.headers.authorization, `Bearer ${connection.apiKey}`);
    res.writeHead(307, { Location: `${destination}/mcp/` });
    res.end();
  });
  const client = new McpConnection(connection, 3000, loopbackFetch(source));
  try {
    await assert.rejects(client.connect(), (error) => {
      assert.equal(error.uncertain, true);
      assert(!error.message.includes(connection.apiKey));
      return true;
    });
    assert.equal(sourceRequests, 1);
    assert.equal(destinationRequests, 0);
  } finally {
    await client.close();
  }
});

test("an unresponsive HTTP request is bounded and never interpreted as execution timeout", async (t) => {
  let requests = 0;
  const origin = await server(t, () => {
    requests++;
  });
  const client = new McpConnection(connection, 200, loopbackFetch(origin));
  try {
    await assert.rejects(client.connect(), (error) => {
      assert.equal(error.uncertain, true);
      assert.match(error.code, /^(TRANSPORT|MCP_REQUEST)_UNCONFIRMED$/);
      assert(!error.message.includes(connection.apiKey));
      return true;
    });
    assert.equal(requests, 1);
  } finally {
    await client.close();
  }
});

test("unverified protocol and empty key fail before any network request", () => {
  let requests = 0;
  const fetcher = async () => {
    requests++;
    throw new Error("must not connect");
  };
  assert.throws(
    () =>
      new McpConnection(
        { ...connection, protocol: "2026-07-28" },
        3000,
        fetcher,
      ),
    (error) => error.code === "PROTOCOL_UNSUPPORTED",
  );
  assert.throws(
    () => new McpConnection({ ...connection, apiKey: " " }, 3000, fetcher),
    (error) => error.code === "AUTHENTICATION_FAILED",
  );
  assert.equal(requests, 0);
});

const canonical = {
  executionId: "11111111-1111-4111-8111-111111111111",
  projectId: "p",
  version: 1,
  status: "succeeded",
  terminal: true,
  cancelRequested: true,
  supportsCancel: false,
  resultVisibility: "json",
  result: { answer: 42 },
  error: null,
  clientId: "client",
  runId: "run",
  acceptedAt: null,
  startedAt: null,
  finishedAt: null,
};

test("REST execution, replay, observation and cancellation preserve authoritative snapshots", async () => {
  const calls = [];
  let reply = canonical;
  const rest = new RestConnection(connection, 3000, async (url, init) => {
    calls.push({ url: String(url), method: init.method });
    return new Response(
      JSON.stringify({
        code: "0000",
        data: { executionId: reply.executionId, snapshot: reply },
      }),
    );
  });
  const args = {
    projectId: "p",
    version: 1,
    params: {},
    idempotencyKey: "key",
    capabilityClass: "service-http-read",
  };
  assert.deepEqual(await rest.call("astron_workflow_execute", args), canonical);
  assert.deepEqual(
    await rest.call("astron_execution_get", canonical),
    canonical,
  );
  assert.deepEqual(
    await rest.call("astron_execution_cancel", canonical),
    canonical,
  );
  for (const change of [
    { status: "running", terminal: false, supportsCancel: true },
    {
      status: "unknown",
      terminal: false,
      error: { code: "CLIENT_RESTARTED", message: "unknown" },
    },
    {
      status: "timeout",
      terminal: true,
      error: { code: "EXECUTION_TIMEOUT", message: "stopped" },
    },
    { result: null, resultVisibility: "suppressed-for-secret-inputs" },
  ]) {
    reply = { ...canonical, ...change };
    assert.deepEqual(await rest.call("astron_execution_get", canonical), reply);
  }
  assert.equal(calls[0].method, "POST");
  assert.match(calls[0].url, /workflows\/execute-async\?contract=1$/);
  assert.match(calls[2].url, /executions\/[^/]+\/cancel$/);
});

test("REST refuses a legacy receipt or mismatched execution without inventing state", async () => {
  for (const data of [
    { executionId: canonical.executionId },
    {
      snapshot: {
        ...canonical,
        executionId: "22222222-2222-4222-8222-222222222222",
      },
    },
  ]) {
    const rest = new RestConnection(
      connection,
      1000,
      async () => new Response(JSON.stringify({ code: "0000", data })),
    );
    await assert.rejects(rest.call("astron_execution_get", canonical));
  }
});

test("REST integration discovery queries the server instead of claiming client support", async () => {
  let requests = 0;
  const integration = {
    contractVersion: 1,
    client: { state: "offline", protocol: null, supportsCancel: false },
  };
  const rest = new RestConnection(connection, 1000, async (url) => {
    requests++;
    assert.match(String(url), /workflows\/integration$/);
    return new Response(JSON.stringify({ code: "0000", data: integration }));
  });
  assert.deepEqual(await rest.call("astron_integration_get", {}), integration);
  assert.equal(requests, 1);
});

test("REST preserves safe admission codes without copying remote detail", async () => {
  for (const code of [
    "READ_CONSTRAINT_INVALID",
    "TRANSPORT_NOT_ALLOWED",
    "EXECUTION_NOT_FOUND",
  ]) {
    const rest = new RestConnection(
      connection,
      1000,
      async () =>
        new Response(
          JSON.stringify({ detail: { code, message: "synthetic-secret" } }),
          { status: 403 },
        ),
    );
    await assert.rejects(
      rest.call("astron_execution_get", canonical),
      (error) => {
        assert.equal(error.code, code);
        assert(!error.message.includes("synthetic-secret"));
        return true;
      },
    );
  }
});
