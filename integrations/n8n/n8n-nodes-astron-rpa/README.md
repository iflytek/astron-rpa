# AstronRPA community node (development)

Control published AstronRPA workflows through authenticated HTTPS MCP: discover workflows, start an execution, wait for its result, query its state and request cancellation.

## Scope and requirements

- This development package provides the common execution framework for individually approved workflows with `supportScope: controlled-validation`. An approved workflow does not establish support for an entire RPA capability family.
- The verified host configuration is self-hosted n8n `2.36.9`, Node.js `24+`, one OpenAPI connection owner and one Windows client matching the repository, with managed client protocol `1`. The package declares `n8n-workflow >=2.36.4 <3`; other host versions, queue mode, multiple replicas or terminals, n8n Cloud and older clients are not covered by this validation.
- OpenAPI must provide integration contract `1`, profile schema `1` and MCP `2025-11-25`. MCP is the primary channel. A published capability may explicitly allow the REST auxiliary transport; the node never switches transports after an uncertain start.
- Capability declarations include a stable `capabilityClass`, `capabilities`, `componentOperations` and `allowedTransports`. The node has independent validators for `json-data`, reviewed service/browser reads and `office-file`. A declaration describes a workflow; it does not add an adapter for unsupported Engine operations.
- Control inputs and outputs use bounded JSON. Files use authorized handles and separate binary transfer for approved `office-file` workflows. Runtime objects, arbitrary local paths and general desktop/UI automation are not exposed. JSON limits are 1 MiB encoded JSON, depth 12, 200 object properties, 1,000 array items and 100,000 characters per string. The server profile is authoritative; the node rejects a mismatched limit contract.

The package requires Node.js `>=24`. The [official n8n `2.36.9` Dockerfile](https://github.com/n8n-io/n8n/blob/n8n%402.36.9/docker/images/n8n/Dockerfile) pins its runtime base to Node.js `24.18.1`, which meets this requirement. Before installation, check the Node version **inside your n8n container**, for example with `docker exec YOUR_N8N_CONTAINER node --version`; the host machine's Node version does not determine the container runtime. Older images with Node.js 20 or 22 do not meet this package's requirement.

## Build, install and connect

From this package directory, independently of the frontend workspace:

```sh
npm ci
npm run typecheck
npm run lint
npm run format:check
npm test
npm pack
```

Install the generated tarball in your self-hosted n8n community package directory and restart n8n. In the **AstronRPA** node, select **AstronRPA MCP API** credentials:

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| MCP Endpoint | Complete HTTPS URL ending in `/mcp/`, including the deployment's path |
| API Key      | The workflow owner's Bearer API key                                   |
| MCP Protocol | `2025-11-25`                                                          |

TLS verification remains enabled. URL credentials, query strings and redirects are rejected. The connection test performs discovery and readiness reads only; an empty workflow list or an offline desktop does not invalidate authentication.

If your AstronRPA deployment exposes only HTTP, such as `http://IP:32742`, configure TLS termination at the gateway or a reverse proxy first and use its HTTPS `/mcp/` endpoint. The certificate must be trusted by the n8n runtime; an HTTP endpoint cannot be used directly. See the repository's [HTTPS deployment guide](../../../docker/HTTPS_DEPLOYMENT.md).

Start the Windows client through its desktop application. Starting Scheduler separately can leave desktop-dependent workflows unable to run.

## Run a workflow

1. Have the server administrator approve the published workflow version through `INTEGRATION_POLICY_FILE`. Connection success alone does not grant execution admission.
2. Use **List Workflows** and **Get Workflow** to obtain the project ID, published version, input schema and admission result.
3. Select **Execute**, enter that project/version and JSON inputs, and choose a mode. Supply a stable, non-secret business key when recovery across n8n executions is required.
4. Keep the returned `executionId` for querying or cancellation.

| Operation        | Behavior                                                                          |
| ---------------- | --------------------------------------------------------------------------------- |
| List Workflows   | One page per input item with `workflows` and `nextOffset`, including empty pages  |
| Get Workflow     | Current published version, input schema, declaration and admission reason         |
| Execute / Async  | Return the accepted execution identity; acceptance does not mean completion       |
| Execute / Wait   | Start once and wait durably for the same execution                                |
| Execute / Sync   | Use the same execution path with a wait budget capped at 30 seconds               |
| Get Execution    | Return the actual state, including failed or unknown outcomes                     |
| Cancel Execution | Request cancellation of the exact ID; query again to confirm the terminal outcome |
| Upload File      | Upload one n8n Binary Data property and return an owner-scoped file handle        |
| Download File    | Download an authorized handle into an n8n Binary Data property                    |
| Delete File      | Remove an owned file after all active execution grants have ended                 |

Execution inputs preserve zero, false, null, arrays and objects. n8n expressions are evaluated when preparing the request; the resulting JSON values are fixed for that execution. Results stay in `result`; arrays are not expanded into additional items. Output includes execution/project/version identity, state, terminal flag, timestamps and cancellation state.

A workflow with secret inputs suppresses the entire RPA result: `resultVisibility: suppressed-for-secret-inputs` explains a null result. This does **not** redact inputs from n8n's execution storage. Store API keys in credentials, not workflow inputs.

### Execution data retention

Wait and Sync create a child execution with `saveDataSuccessExecution: "all"` and `saveDataErrorExecution: "all"`. Its input and waiting checkpoints contain the prepared request, including parameters marked as secret in AstronRPA. These values can remain in n8n execution records after completion; disabling successful execution storage only on the parent workflow does not disable the child's explicit setting. Async inputs can also be retained under the parent workflow's settings.

Restrict access to n8n execution records and backups, and enable execution-data pruning on the n8n host. For example, adjust these settings to your retention requirements:

```env
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
EXECUTIONS_DATA_PRUNE_MAX_COUNT=10000
```

`EXECUTIONS_DATA_MAX_AGE` is measured in hours. Pruning eligible finished executions limits retention; it is not immediate secret redaction and does not remove copies in backups. Keep waiting checkpoints available until their executions are resolved, since durable recovery needs the saved request and execution identity. See [n8n execution-data configuration](https://docs.n8n.io/hosting/configuration/environment-variables/executions/).

### Capability boundary

Use **Get Workflow** before execution and verify `profile.capabilityClass`, `profile.componentOperations`, `profile.allowedTransports` and `profile.admission.allowed`. The node does not infer a capability from a workflow name or component name. Browser, HTTP, database, mail and shared-service reads require a complete operation-level declaration. Mixed workflows must satisfy every applicable constraint; approval for one category never grants another. The reserved `service-openapi-read` identifier has no approved operations: current Engine OpenAPI operations require files and belong to the Office/file category.

Select **MCP (Primary)** unless the published declaration explicitly includes `rest` in `allowedTransports` and the operation has a documented REST auxiliary route. REST is never an automatic fallback for an uncertain MCP request.

Read workflows require `readContractVersion: 1` from an administrator-reviewed release. HTTP permits GET/HEAD without upload or save; mail preserves unread state and does not save attachments; browser extraction stays on one page without export; database SQL is fixed and reviewed with read-only credentials. The review is not a sandbox for arbitrary Python or SQL. Connection objects, element handles and generators remain inside the workflow, and results use the shared bounded JSON contract. REST submission, observation and cancellation preserve the server's execution identity, state and result visibility.

Configure the published RPA workflow for the capability it declares:

- **Browser:** use the intended active tab with the AstronRPA extension connected, and reserve the terminal during execution. Set `activate_window=False` on every `BrowserSoftware.get_current_obj` call to avoid activating or maximizing a window. Have the administrator include that value in the [read-only admission review](../../../backend/openapi-service/README.md#integration-admission); after changing workflow arguments, republish and update the version-bound review.
- **Mail:** leave `mask_as_read_flag` and `save_attachment_flag` disabled. An unread-only query can return the same messages on later runs, so handle deduplication in the calling workflow. General mail-component usage and guidance for workflows that consume unread mail are in the [FAQ](../../../FAQ.md#q-why-do-unread-only-mail-queries-return-the-same-messages).
- **Database:** use read-only credentials and fixed, reviewed SQL. For SQLite, set `connect_info.read_only: true`. MySQL uses the packaged driver; other database types require the [corresponding optional driver](../../../FAQ.md#q-which-drivers-do-database-workflows-need) in the executing client's Python environment. A successful SQLite test does not establish compatibility with those database deployments.

### JSON data workflow boundary

Use **Get Workflow** before execution and verify `profile.capabilityClass` is `json-data`, `profile.admission.allowed` is `true`, and the returned `inputSchema` matches the data being sent. JSON values preserve `0`, `false`, `null`, arrays and nested objects. Unknown fields, non-finite numbers, runtime objects, file values and values over the published limits are rejected before dispatch.

The result remains one JSON value under `result`; arrays are not expanded into n8n items. An optional declared `outputSchema` documents the result shape, but it does not enable file, GUI or runtime-object capabilities. Browser/service reads use their own peer capability module and declaration.

### Office and file workflows

The server administrator must configure persistent file storage and an HTTPS transfer endpoint, and approve the published workflow's `fileContract` and private file review. The Windows client must advertise `fileTransferVersion: 1`. See [server file configuration](../../../backend/openapi-service/README.md#office-and-file-workflows).

An importable [file workflow example](examples/office-file.json) demonstrates the binary upload, execution and download sequence. DataTable exports support CSV, XLSX and JSON; use XLSX for spreadsheet output because the openpyxl backend cannot write legacy XLS files. CSV export writes the cell values held by openpyxl; formula cells are exported as their stored formula expressions rather than recalculated results.

1. Use **Upload File** with the incoming Binary Property (default `data`). Its output contains `fileId`, `fileName`, `size`, `sha256` and `expiresAt`; it contains no local path or transfer credential.
2. Select **Execute**, preferably through MCP, with the approved `office-file` project/version. Bind input file parameters to uploaded IDs and output parameters to `output:<parameterName>`. For example, a contract with input `source` and output `target` accepts `{"source":"<fileId>","target":"output:target"}`. Set an RPA Deadline between 1 and 3,600 seconds.
3. Wait for confirmed success. The result is `{ "data": <workflow JSON>, "files": { "target": <file metadata> } }`. Exact file-parameter path echoes are omitted from `data`; other workspace paths are rejected. Pass `result.files.target.fileId` to **Download File** to obtain Binary Data for subsequent n8n nodes.
4. Use **Delete File** after the file is no longer needed, or let it expire. A file with an active execution grant cannot be deleted. Downloads and reuse of output handles require the original execution to have succeeded and its workflow to remain authorized.

File transfer always uses the HTTPS REST routes adjacent to the configured MCP endpoint; this does not change the execution transport or enable automatic fallback. Upload retries within the same n8n execution/node/run/item use the same key and require identical bytes. A new n8n execution creates a new upload. Downloaded bytes are checked against the returned size and SHA-256.

Limits are 10 MiB per file, eight input and output bindings combined per execution, and 24-hour server retention. A user may hold at most 64 records and 100 MiB of allocated storage; pending uploads reserve the maximum file size. Expired records are swept every five minutes. Temporary client transfers are bound to the execution and expire after its deadline plus a short recovery allowance. Keep handles available until waiting executions have resolved; n8n's own execution/binary storage has a separate retention policy.

The client downloads inputs into an execution-specific directory and replaces output placeholders with private paths. Workflows must use those paths, return bounded JSON summaries and close all resources; local workspace paths cannot be returned as results. Office runs require an installed, compatible Excel/Word or WPS COM provider, use private instances and disable macros. Do not use global Office close/kill options, clipboard operations or attachment to a user's open document. Archive extraction rejects traversal and links; managed archives are limited to 512 members, 10 MiB per member and 80 MiB expanded data. Reviewed external transfers still require the relevant service credentials and destination restrictions. File workflows accepting secret-marked parameters are currently rejected, since binary artifacts cannot use the ordinary result-suppression mechanism.

## Capability layout

The node invokes published workflows through the common transport and execution framework. Capability modules are peers and validate declarations; they do not call Engine components directly or inherit another category's validator.

```text
n8n-nodes-astron-rpa/
|-- credentials/                 # Shared credential handling
|-- nodes/                       # Shared n8n entry point
|-- transport/                  # MCP primary / explicit REST auxiliary
|-- execution/                  # Shared lifecycle, idempotency and recovery
|-- mapping/                    # Shared JSON values, snapshots and errors
|-- capabilities/
|   |-- json-data.ts             # JSON/data declaration checks
|   |-- browser-service.ts       # Browser/service read declaration checks
|   |-- office-file.ts           # Office/file declaration checks
|   `-- shared/
|       |-- types.ts             # Wire identifiers and profile types
|       |-- catalog.ts           # 26 components -> five peer capability groups
|       `-- registry.ts           # Dispatch to the matching capability module
|-- tests/
`-- examples/
```

`shared/catalog.ts` maps component operations to categories; it does not create a separate node for each component. A component may span several groups. Control-flow markers do not grant access to the operations nested inside them. Group names describe source organization; `capabilityClass` identifies the wire contract.

| Peer group / module            | Component coverage by operation                                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `json-data.ts`                 | dataprocess, datatable, encrypt, report, reviewed script                                                                  |
| `browser-service.ts`           | browser, network, database, email, enterprise reads                                                                       |
| `office-file.ts`               | datatable, browser, email, enterprise, excel, network, openapi, pdf, system, word file operations                         |
| `desktop-ui.ts` (planned)      | browser, cua, dialog, input, software, system, verifycode, vision, window, winelement interaction                         |
| `ai-dynamic-risk.ts` (planned) | ai, browser, cua, database, email, enterprise, network, script, smart, verifycode, vision dynamic or high-risk operations |

Future modules belong beside `json-data.ts` and `browser-service.ts`, use the shared registry and common framework, and do not import a previous category's implementation. Planned names are documentation only; no empty modules or unsupported handlers are registered. Catalog coverage is an inventory, not a claim that every listed operation has been implemented or verified. Shared utilities should stay neutral; server/client defects belong in their original modules.

For JSON-data executions, the service freezes the output schema and JSON limits at acceptance and checks successful results before persistence. A result over the byte limit or outside the schema becomes `failed / UNSUPPORTED_RESULT`, with no business payload stored. The byte limit measures the compact UTF-8 encoding of the business result; execution IDs, status and other envelope fields do not consume its allowance. The node validates result values separately from that metadata, so an exact 1 MiB result remains readable.

## Execution behavior and limits

### Idempotency and retries

Every start has an idempotency key. Automatic keys are isolated by n8n execution, node, run and input item. **A new n8n execution or manual rerun creates a new key.** To recover an existing request across executions, use its original business key, version, inputs, RPA deadline and declaration revision. Changed request content produces a conflict.

If publication or admission changed, **Frozen Declaration Revision** accepts the original `correlation.profileRevision` with the complete original request and business key. The server rechecks authorization and returns an existing matching receipt; the revision does not authorize an unapproved new start.

On n8n `2.36.9`, **Retry On Fail does not rerun a business failure returned by durable waiting**. Same-key recovery returns the original failed receipt. Intentionally running the business operation again requires a new key.

### Waiting, cancellation and batches

| Setting             | Effect                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------- |
| MCP Request Timeout | Bound one network request; does not establish the RPA outcome                                 |
| Wait Budget         | Stop waiting and retain any known execution ID; does not stop RPA                             |
| RPA Deadline        | Request process stop after the execution deadline; `timeout` requires confirmed stop evidence |

Wait processes input items sequentially. An unknown or unresolved prior execution blocks later starts, even with Continue On Fail. A confirmed failure may continue to the next item when continuation is enabled. Async submits sequentially without waiting for desktop availability; a busy client is not an implicit queue.

Cancel targets the specified execution. A cancellation request is not proof of completion, and stopping a process does not undo business effects already performed.

### Recovery and errors

Waiting checkpoints can resume after an n8n restart. Resumption may be delayed by n8n's waiting-execution scan. Arbitrary crashes during an active step and migration of waiting executions between package versions are outside this recovery guarantee. Preserve execution data until in-flight work is resolved, and resolve waiting executions before upgrading or rolling back the node.

An `unknown` state does not confirm that a task stopped. Recover through the original ID or original request/business key; do not switch transports or create a new key solely because a response was lost.

Execute failures follow Stop/Continue/error-output settings. Query and Cancel return snapshots as data. On the error branch, `$json.error` contains a JSON envelope with the safe execution identity; read a known ID with `JSON.parse($json.error).executionId`. Errors before acceptance may have no ID.

Ordinary republication preserves management of accepted executions. Workflow deletion, ownership changes, external-access disablement and API key revocation still deny access.

This also changes the existing REST behavior: after a workflow is republished, `GET /executions/{execution_id}` can still return a previously accepted execution with its original version, instead of rejecting it solely because the published version changed. `GET /executions/get` likewise includes eligible executions from earlier published versions. Ownership, external-access and API-key checks remain in force. Starting a new execution still requires the current published version; querying an old execution does not authorize a new start of that old version.

## Repository documentation

- [Server admission configuration](../../../backend/openapi-service/README.md#integration-admission)
- [Example workflow](examples/README.md)
- [Validation results and incomplete checks](../VALIDATION.md)

These references are in the source repository. Validation procedures, environment details and execution evidence are maintained in the validation record.
