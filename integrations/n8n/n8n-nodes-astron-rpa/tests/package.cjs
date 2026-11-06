// Verify the artifact as a consumer, without the source tree's overrides or dev dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { createRequire } = require("node:module");

const root = path.resolve(__dirname, "..");
const manifest = require("../package.json");
const tempRoot = fs.realpathSync(os.tmpdir());
const workspace = fs.mkdtempSync(path.join(tempRoot, "astron-n8n-package-"));
const npmCli = process.env.npm_execpath;
assert(npmCli, "Run through npm run test:package");
const npm = (cwd, args) =>
  execFileSync(process.execPath, [npmCli, ...args], {
    cwd,
    encoding: "utf8",
    timeout: 180000,
    stdio: ["ignore", "pipe", "pipe"],
  });

function sourceModules(directory) {
  return fs
    .readdirSync(path.join(root, directory), { withFileTypes: true })
    .flatMap((entry) => {
      const relative = `${directory}/${entry.name}`;
      if (entry.isDirectory()) return sourceModules(relative);
      if (
        !entry.isFile() ||
        !entry.name.endsWith(".ts") ||
        entry.name.endsWith(".d.ts")
      )
        return [];
      assert(
        !/(?:^|\/)(?:tests?|fixtures)(?:\/|$)|\.(?:test|spec)\.ts$/.test(
          relative,
        ),
        `Test source must stay outside runtime directories: ${relative}`,
      );
      return [`dist/${relative.slice(0, -3)}.js`];
    });
}

async function main() {
  const [packed] = JSON.parse(
    npm(root, [
      "pack",
      "--ignore-scripts",
      "--json",
      "--pack-destination",
      workspace,
    ]),
  );
  const files = new Set(packed.files.map((file) => file.path));
  const exampleFiles = [
    "desktop-ui.json",
    "execute-and-query.json",
    "office-file.json",
  ];
  // Check the actual packed files, including stale or accidentally copied build
  // output. Repository evidence, tests, TS sources and host configuration stay out.
  const expectedOwnFiles = new Set([
    "package.json",
    "README.md",
    "LICENSE",
    "dist/package.json",
    "examples/README.md",
    ...exampleFiles.map((file) => `examples/${file}`),
    ...[
      "capabilities",
      "credentials",
      "execution",
      "mapping",
      "nodes",
      "transport",
    ].flatMap(sourceModules),
  ]);
  const ownFiles = [...files].filter(
    (file) => !file.startsWith("node_modules/"),
  );
  assert.deepEqual(
    ownFiles.sort(),
    [...expectedOwnFiles].sort(),
    "Unexpected or missing project files in the release tarball",
  );
  for (const file of [...manifest.n8n.nodes, ...manifest.n8n.credentials])
    assert(files.has(file), `Missing n8n entry point: ${file}`);
  assert(files.has("node_modules/@modelcontextprotocol/sdk/package.json"));
  assert(
    ![...files].some((file) =>
      /^(tests|node_modules\/n8n-workflow)\//.test(file),
    ),
  );
  assert(
    !/\]\(\.\.\//.test(fs.readFileSync(path.join(root, "README.md"), "utf8")),
    "Published README must not reference files outside its package",
  );
  for (const file of exampleFiles) {
    const workflow = JSON.parse(
      fs.readFileSync(path.join(root, "examples", file), "utf8"),
    );
    assert.equal(workflow.active, false, `${file} must import inactive`);
    assert(
      workflow.nodes.every((node) => node.credentials === undefined),
      `${file} must not include credential bindings`,
    );
    for (const node of workflow.nodes.filter((node) =>
      node.type.endsWith(".astronRpa"),
    ))
      assert.equal(node.type, `${manifest.name}.astronRpa`);
  }
  const consumer = path.join(workspace, "consumer");
  fs.mkdirSync(consumer);
  fs.writeFileSync(
    path.join(consumer, "package.json"),
    JSON.stringify({
      name: "astron-package-consumer",
      version: "1.0.0",
      private: true,
    }),
  );
  // n8n provides the peer at runtime; keep its dependency audit separate here.
  npm(consumer, [
    "install",
    "--ignore-scripts",
    "--omit=dev",
    "--omit=peer",
    "--no-fund",
    path.join(workspace, packed.filename),
  ]);
  npm(consumer, [
    "audit",
    "--omit=dev",
    "--omit=peer",
    "--audit-level=moderate",
  ]);
  const installed = path.join(
    consumer,
    "node_modules",
    ...manifest.name.split("/"),
  );
  const installedManifest = JSON.parse(
    fs.readFileSync(path.join(installed, "package.json"), "utf8"),
  );
  assert.equal(installedManifest.name, manifest.name);
  assert.equal(installedManifest.version, manifest.version);
  const installedRequire = createRequire(path.join(installed, "package.json"));
  const sdkRequire = createRequire(
    installedRequire.resolve("@modelcontextprotocol/sdk/client/index.js"),
  );
  assert.equal(sdkRequire("zod/package.json").version, "4.6.7");
  const { McpConnection } = require(
    path.join(installed, "dist/transport/mcp.js"),
  );
  const client = new McpConnection(
    {
      endpoint: "https://rpa.example.com/mcp/",
      apiKey: "synthetic",
      protocol: "2025-11-25",
    },
    1000,
    async (_url, init) => {
      const request = init.body ? JSON.parse(init.body) : {};
      if (request.id === undefined) return new Response(null, { status: 202 });
      let result;
      if (request.method === "initialize") {
        assert.deepEqual(request.params.clientInfo, {
          name: manifest.name,
          version: manifest.version,
        });
        result = {
          protocolVersion: "2025-11-25",
          capabilities: { tools: {} },
          serverInfo: { name: "synthetic", version: "1" },
        };
      } else {
        result = {
          content: [
            { type: "text", text: JSON.stringify({ installed: true }) },
          ],
        };
      }
      return Response.json({ jsonrpc: "2.0", id: request.id, result });
    },
  );
  try {
    await client.connect();
    assert.deepEqual(await client.call("astron_integration_get", {}), {
      installed: true,
    });
  } finally {
    await client.close();
  }
  console.log(
    `Package contents (${ownFiles.length} project files), installation, runtime dependency audit and MCP smoke passed: ${manifest.name}@${manifest.version}`,
  );
}

main()
  .catch((error) => {
    console.error(error.message);
    if (error.stdout) console.error(error.stdout);
    if (error.stderr) console.error(error.stderr);
    process.exitCode = 1;
  })
  .finally(() => {
    assert(
      path.dirname(workspace) === tempRoot &&
        path.basename(workspace).startsWith("astron-n8n-package-"),
    );
    fs.rmSync(workspace, { recursive: true, force: true });
  });
