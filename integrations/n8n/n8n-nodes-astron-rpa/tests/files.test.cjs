const { test } = require("node:test");
const assert = require("node:assert/strict");
const { createHash, randomUUID } = require("node:crypto");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { FileConnection } = require("../dist/transport/files");
const {
  FILE_LIMITS,
  validateOfficeFileProfile,
  safeFileName,
} = require("../dist/capabilities/office-file");
const {
  validateCapabilityProfile,
} = require("../dist/capabilities/shared/registry");
const {
  OFFICE_FILE_OPERATIONS,
  COMPONENT_COVERAGE,
} = require("../dist/capabilities/shared/catalog");
const { AstronRpa } = require("../dist/nodes/AstronRpa/AstronRpa.node");

test("node and server publish the same Office/file operation inventory", () => {
  const source = readFileSync(
    resolve(
      __dirname,
      "../../../../backend/openapi-service/app/schemas/office_file.py",
    ),
    "utf8",
  );
  const serverOperations = [
    ...source.matchAll(/"([A-Z][A-Za-z]+\.[a-z_]+)"/g),
  ].map((match) => match[1]);
  assert.deepEqual([...OFFICE_FILE_OPERATIONS].sort(), serverOperations.sort());
});

const connection = {
  endpoint: "https://rpa.example/api/rpa-openapi/mcp",
  apiKey: "test-key",
};
const metadata = (data, name = "测试.txt") => ({
  fileId: randomUUID(),
  fileName: name,
  size: data.length,
  sha256: createHash("sha256").update(data).digest("hex"),
  expiresAt: Date.now() / 1000 + 3600,
});
const profile = () => ({
  capabilityClass: "office-file",
  capabilities: ["office-file"],
  componentOperations: ["File.file_read", "File.file_write"],
  allowedTransports: ["mcp"],
  fileInputs: true,
  fileOutputs: true,
  requiresGui: false,
  requiresHuman: false,
  exclusiveTerminal: true,
  risk: "medium",
  sideEffects: ["workspace-files"],
  fileContract: {
    version: 1,
    limits: FILE_LIMITS,
    inputs: { source: [".txt"] },
    outputs: { target: "result.txt" },
  },
});

test("node Binary Data helpers preserve item identity, retry key and downloaded bytes", async () => {
  const saved = [
    FileConnection.prototype.upload,
    FileConnection.prototype.download,
  ];
  const data = Buffer.from([0, 255, 1]);
  const result = metadata(data);
  let operation = "uploadFile",
    run = 0;
  const keys = [];
  const context = {
    getNodeParameter: (name, _index, fallback) =>
      ({ operation, binaryProperty: "document", fileId: result.fileId })[
        name
      ] ?? fallback,
    getInputData: () => [{ json: {} }, { json: {} }],
    getCredentials: async () => connection,
    getInstanceId: () => "instance",
    getExecutionId: () => "execution",
    getNode: () => ({ id: "node", name: "AstronRPA" }),
    getWorkflowDataProxy: () => ({ $runIndex: run }),
    helpers: {
      assertBinaryData: (_i, property) => {
        assert.equal(property, "document");
        return { fileName: result.fileName };
      },
      getBinaryDataBuffer: async () => data,
      prepareBinaryData: async (bytes, name) => {
        assert.deepEqual(bytes, data);
        assert.equal(name, result.fileName);
        return { data: "stored-binary", mimeType: "application/octet-stream" };
      },
    },
  };
  FileConnection.prototype.upload = async (name, bytes, key) => {
    assert.equal(name, result.fileName);
    assert.deepEqual(bytes, data);
    keys.push(key);
    return result;
  };
  FileConnection.prototype.download = async () => ({ metadata: result, data });
  try {
    const node = new AstronRpa();
    const [uploaded] = await node.execute.call(context);
    assert.deepEqual(
      uploaded.map((item) => item.pairedItem),
      [{ item: 0 }, { item: 1 }],
    );
    await node.execute.call(context);
    assert.equal(keys[0], keys[2]);
    assert.notEqual(keys[0], keys[1]);
    run = 1;
    await node.execute.call(context);
    assert.notEqual(keys[0], keys[4]);
    operation = "downloadFile";
    const [downloaded] = await node.execute.call(context);
    assert.equal(downloaded[0].binary.document.data, "stored-binary");
    assert.deepEqual(downloaded[1].pairedItem, { item: 1 });
  } finally {
    [FileConnection.prototype.upload, FileConnection.prototype.download] =
      saved;
  }
});

test("response stream errors cannot expose remote diagnostics", async () => {
  const client = new FileConnection(
    connection,
    1000,
    async () =>
      new Response(
        new ReadableStream({
          start(controller) {
            controller.error(new Error("secret diagnostic"));
          },
        }),
      ),
  );
  await assert.rejects(
    client.upload("test.txt", Buffer.from("x"), "key"),
    /FILE_TRANSFER_UNCONFIRMED/,
  );
});

test("office-file is an independent peer capability with explicit file and GUI boundaries", () => {
  assert.deepEqual(validateCapabilityProfile(profile()), profile());
  for (const change of [
    { requiresHuman: true },
    { exclusiveTerminal: false },
    { fileOutputs: false },
    { componentOperations: ["Process.run_command"] },
    { allowedTransports: [] },
    { risk: "high" },
  ])
    assert.throws(() => validateOfficeFileProfile({ ...profile(), ...change }));
  assert.throws(() =>
    validateOfficeFileProfile({
      ...profile(),
      componentOperations: ["Excel.open_excel"],
    }),
  );
  validateOfficeFileProfile({
    ...profile(),
    requiresGui: true,
    componentOperations: ["Excel.open_excel"],
  });
  assert(
    COMPONENT_COVERAGE.find(
      (c) => c.component === "astronverse-email",
    ).groups.includes("office-file"),
  );
  assert(OFFICE_FILE_OPERATIONS.has("Email.receive_email"));
  assert(!OFFICE_FILE_OPERATIONS.has("System.printer"));
  validateOfficeFileProfile({
    ...profile(),
    requiresGui: true,
    componentOperations: [
      "BrowserSoftware.get_current_obj",
      "BrowserElement.create_element",
      "BrowserElement.screenshot",
    ],
  });
  assert(!OFFICE_FILE_OPERATIONS.has("BrowserElement.click"));
  assert.throws(() =>
    validateOfficeFileProfile({
      ...profile(),
      componentOperations: ["Email.receive_email"],
    }),
  );
  validateOfficeFileProfile({
    ...profile(),
    componentOperations: ["Email.receive_email"],
    sideEffects: ["workspace-files", "external-file-transfer"],
  });
});

test("file uploads preserve bytes and use exact REST paths without redirect or execution fallback", async () => {
  const data = Buffer.from("中文\x00file");
  const result = metadata(data);
  const calls = [];
  const client = new FileConnection(connection, 1000, async (url, init) => {
    calls.push([String(url), init]);
    assert.equal(init.redirect, "error");
    assert.equal(
      new Headers(init.headers).get("Authorization"),
      "Bearer test-key",
    );
    if (init.method === "POST") {
      assert.equal(url.pathname, "/api/rpa-openapi/files");
      assert.deepEqual(JSON.parse(init.body), {
        fileName: "测试.txt",
        uploadKey: "stable-key",
      });
    } else {
      assert.equal(
        url.pathname,
        `/api/rpa-openapi/files/${result.fileId}/content`,
      );
      assert.deepEqual(Buffer.from(init.body), data);
    }
    return Response.json(result);
  });
  assert.deepEqual(await client.upload("测试.txt", data, "stable-key"), result);
  assert.equal(calls.length, 2);
});

test("file download verifies both the handle and content digest", async () => {
  const data = Buffer.from([0, 1, 255]);
  const result = metadata(data);
  const client = new FileConnection(connection, 1000, async (url) =>
    url.pathname.endsWith("/content")
      ? new Response(data)
      : Response.json(result),
  );
  assert.deepEqual(await client.download(result.fileId), {
    metadata: result,
    data,
  });
  const tampered = new FileConnection(connection, 1000, async (url) =>
    url.pathname.endsWith("/content")
      ? new Response("wrong")
      : Response.json(result),
  );
  await assert.rejects(
    tampered.download(result.fileId),
    /FILE_INTEGRITY_FAILED/,
  );
});

test("unsafe names, local paths, oversized files and URL credentials fail before transfer", async () => {
  for (const value of [
    "../escape",
    "C:\\local.txt",
    "C:relative",
    "NUL",
    "file.txt:ads",
    "bad\x00name",
    "file.",
  ])
    assert.throws(() => safeFileName(value));
  for (const endpoint of [
    "http://rpa.example/mcp",
    "https://secret@rpa.example/mcp",
    "https://rpa.example/mcp?key=x",
  ])
    assert.throws(() => new FileConnection({ ...connection, endpoint }, 1000));
  let called = false;
  const client = new FileConnection(connection, 1000, async () => {
    called = true;
    throw new Error("unexpected");
  });
  await assert.rejects(client.download("C:/file.txt"), /FILE_ID_INVALID/);
  await assert.rejects(
    client.upload("big.bin", Buffer.alloc(FILE_LIMITS.maxFileBytes + 1), "key"),
    /FILE_TOO_LARGE/,
  );
  assert.equal(called, false);
});

test("file transport preserves safe denial codes and bounded uncertain failures", async () => {
  const client = new FileConnection(connection, 1000, async () =>
    Response.json(
      { detail: { code: "FILE_IN_USE", message: "secret diagnostic" } },
      { status: 400 },
    ),
  );
  await assert.rejects(
    client.delete(randomUUID()),
    (error) =>
      error.code === "FILE_IN_USE" && !error.message.includes("secret"),
  );
  const uncertain = new FileConnection(connection, 1000, async () => {
    throw new Error("secret diagnostic");
  });
  await assert.rejects(
    uncertain.delete(randomUUID()),
    (error) => error.code === "FILE_TRANSFER_UNCONFIRMED" && error.uncertain,
  );
});
