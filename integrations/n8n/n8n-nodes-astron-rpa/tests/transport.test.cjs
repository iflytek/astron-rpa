const { test } = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const { once } = require("node:events");
const { McpConnection } = require("../dist/transport/mcp");

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
