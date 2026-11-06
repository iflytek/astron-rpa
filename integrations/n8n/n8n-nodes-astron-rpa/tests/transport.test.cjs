const { test } = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const { once } = require("node:events");
const { McpConnection } = require("../dist/transport/mcp");
const { RestConnection } = require("../dist/transport/rest");
const { FileConnection } = require("../dist/transport/files");
const { observedFetch } = require("../dist/transport/correlation");
const { correlationHeaders } = require("../dist/transport/correlation");

const connection = {
  endpoint: "https://rpa.example.com/mcp/",
  apiKey: "synthetic-test-key",
  protocol: "2025-11-25",
};

test("MCP initialization advertises the installed package identity and version", async () => {
  const manifest = require("../package.json");
  const client = new McpConnection(connection, 1000, async (_url, init) => {
    const body = init.body ? JSON.parse(init.body) : {};
    if (body.method !== "initialize")
      return new Response(null, { status: 202 });
    assert.deepEqual(body.params.clientInfo, {
      name: manifest.name,
      version: manifest.version,
    });
    return Response.json({
      jsonrpc: "2.0",
      id: body.id,
      result: {
        protocolVersion: "2025-11-25",
        capabilities: { tools: {} },
        serverInfo: { name: "synthetic", version: "1" },
      },
    });
  });
  try {
    await client.connect();
  } finally {
    await client.close();
  }
});

for (const Transport of [McpConnection, RestConnection]) {
  test(`${Transport.name} preserves only bounded schema diagnostics`, async () => {
    const hint = {
      field: "$/rows/*/count",
      rule: "type",
      expected: ["integer"],
    };
    const error = {
      code: "INVALID_ARGUMENTS",
      message: "private-value",
      validation: { ...hint, instance: "private-value" },
    };
    const client = new Transport(connection, 1000, async (_url, init) => {
      if (Transport === RestConnection)
        return Response.json({ detail: error }, { status: 403 });
      const body = init.body ? JSON.parse(init.body) : {};
      if (body.id === undefined) return new Response(null, { status: 202 });
      return Response.json({
        jsonrpc: "2.0",
        id: body.id,
        result:
          body.method === "initialize"
            ? {
                protocolVersion: "2025-11-25",
                capabilities: { tools: {} },
                serverInfo: { name: "synthetic", version: "1" },
              }
            : {
                isError: true,
                content: [{ type: "text", text: JSON.stringify({ error }) }],
              },
      });
    });
    try {
      await client.connect();
      await assert.rejects(client.call("astron_integration_get", {}), (e) => {
        assert.equal(e.code, "INVALID_ARGUMENTS");
        assert.equal(e.uncertain, false);
        assert.deepEqual(e.validation, hint);
        assert(!JSON.stringify(e).includes("private"));
        return true;
      });
    } finally {
      await client.close();
    }
  });
}

for (const Transport of [McpConnection, RestConnection, FileConnection]) {
  for (const [cause, expected] of [
    ["CERT_HAS_EXPIRED", "TLS_ERROR"],
    ["ECONNREFUSED", "NETWORK_ERROR"],
    ["ETIMEDOUT", "TIMEOUT"],
  ]) {
    test(`${Transport.name} records safe ${expected} correlation without changing uncertainty`, async () => {
      const events = [];
      let sent;
      const client = new Transport(
        {
          ...connection,
          correlation: {
            n8nExecutionId: "parent",
            itemIndex: 0,
            report: (e) => events.push(e),
          },
        },
        1000,
        async (_url, init) => {
          sent = new Headers(init.headers);
          throw new TypeError("synthetic-private-password", {
            cause: Object.assign(new Error("private-body"), { code: cause }),
          });
        },
      );
      try {
        await assert.rejects(
          Transport === McpConnection
            ? client.connect()
            : Transport === FileConnection
              ? client.delete("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
              : client.call("astron_integration_get", {}),
          (e) => e.uncertain === true && !e.message.includes("private"),
        );
        assert.equal(events.length, 1);
        assert.equal(events[0].errorType, expected);
        assert.equal(events[0].traceId, sent.get("X-Request-ID"));
        assert.equal(events[0].targetHost, "rpa.example.com");
        assert.equal(events[0].n8nExecutionId, "parent");
        assert.equal(events[0].itemIndex, 0);
        assert(!JSON.stringify(events).includes(connection.apiKey));
        assert(!JSON.stringify(events).includes("private"));
      } finally {
        if (client.close) await client.close();
      }
    });
  }
}

test("HTTP diagnostics separate authentication, permissions and rate limit and omit URL secrets", async () => {
  const events = [];
  for (const status of [401, 403, 429, 500]) {
    const response = await observedFetch(
      async () => new Response("private-response", { status }),
      "https://user:password@rpa.example.com/private-path?token=private",
      { headers: { Authorization: "Bearer private" } },
      { n8nExecutionId: "parent", itemIndex: 1, report: (e) => events.push(e) },
      "rest",
    );
    assert.equal(response.status, status);
  }
  assert.deepEqual(
    events.map((e) => e.errorType),
    ["HTTP_401", "HTTP_403", "HTTP_429", "HTTP_ERROR"],
  );
  assert(!JSON.stringify(events).includes("private"));
  assert(!JSON.stringify(events).includes("password"));
  assert.equal(new Set(events.map((e) => e.traceId)).size, 4);
});

test("broken diagnostic sink cannot change the transport error or cause another request", async () => {
  const original = new Error("synthetic");
  let calls = 0;
  await assert.rejects(
    observedFetch(
      async () => {
        calls++;
        throw original;
      },
      connection.endpoint,
      {},
      {
        n8nExecutionId: "parent",
        itemIndex: 1,
        report: () => {
          throw new Error("logger failed");
        },
      },
      "mcp",
    ),
    (e) => e === original,
  );
  assert.equal(calls, 1);
});

test("correlation is bounded diagnostics and each HTTP request has a fresh trace", async () => {
  const context = { n8nExecutionId: "parent-123", itemIndex: 2 };
  const seen = [];
  const client = new RestConnection(
    { ...connection, correlation: context },
    1000,
    async (_url, init) => {
      seen.push(new Headers(init.headers));
      return Response.json({ code: "0000", data: {} });
    },
  );
  await client.call("astron_integration_get", {});
  await client.call("astron_integration_get", {});
  assert.equal(seen[0].get("X-N8N-Execution-ID"), "parent-123");
  assert.equal(seen[0].get("X-N8N-Item-Index"), "2");
  assert.notEqual(seen[0].get("X-Request-ID"), seen[1].get("X-Request-ID"));
  assert.deepEqual(
    Object.keys(
      correlationHeaders({ n8nExecutionId: "bad\nvalue", itemIndex: -1 }),
    ),
    ["X-Request-ID"],
  );
  assert.equal(context.n8nExecutionId, "parent-123");
});

test("MCP sends correlation on initialization and tool calls without changing RPC content", async () => {
  const calls = [];
  const client = new McpConnection(
    { ...connection, correlation: { n8nExecutionId: "parent", itemIndex: 0 } },
    1000,
    async (_url, init) => {
      const headers = new Headers(init.headers);
      const body = init.body ? JSON.parse(init.body) : {};
      calls.push({ headers, body });
      assert.equal(headers.get("X-N8N-Execution-ID"), "parent");
      assert.equal(headers.get("X-N8N-Item-Index"), "0");
      if (body.id === undefined) return new Response(null, { status: 202 });
      return Response.json({
        jsonrpc: "2.0",
        id: body.id,
        result:
          body.method === "initialize"
            ? {
                protocolVersion: "2025-11-25",
                capabilities: { tools: {} },
                serverInfo: { name: "synthetic", version: "1" },
              }
            : { content: [{ type: "text", text: '{"ok":true}' }] },
      });
    },
  );
  try {
    await client.connect();
    assert.deepEqual(await client.call("astron_integration_get", {}), {
      ok: true,
    });
    const invocation = calls.find(({ body }) => body.method === "tools/call");
    assert.deepEqual(invocation.body.params.arguments, {});
    assert.equal(
      new Set(calls.map(({ headers }) => headers.get("X-Request-ID"))).size,
      calls.length,
    );
  } finally {
    await client.close();
  }
});

test("confirmed rate limiting is not an uncertain dispatch or transport fallback", async () => {
  for (const Transport of [McpConnection, RestConnection]) {
    let count = 0;
    const client = new Transport(connection, 1000, async () => {
      count++;
      return Response.json(
        { detail: { code: "RATE_LIMITED" } },
        { status: 429 },
      );
    });
    try {
      await assert.rejects(
        Transport === McpConnection
          ? client.connect()
          : client.call("astron_integration_get", {}),
        (error) => error.code === "RATE_LIMITED" && !error.uncertain,
      );
      assert.equal(count, 1);
    } finally {
      await client.close();
    }
  }
});

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
