# AstronRPA community node (development)

Control published AstronRPA workflows through authenticated HTTPS MCP: discover workflows, start an execution, wait for its result, query its state and request cancellation.

## Scope and requirements

- This development package provides the common execution framework for individually approved workflows with `supportScope: controlled-validation`. An approved workflow does not establish support for an entire RPA capability family.
- The verified host configuration is self-hosted n8n `2.36.9`, Node.js `24+`, one OpenAPI connection owner and one Windows client matching the repository, with managed client protocol `1`. The package declares `n8n-workflow >=2.36.4 <3`; other host versions, queue mode, multiple replicas or terminals, n8n Cloud and older clients are not covered by this validation.
- OpenAPI must provide integration contract `1`, profile schema `1` and MCP `2025-11-25`. All node business operations use MCP with the existing API key authentication.
- The first classified capability is `json-data`: its declaration must include `capabilityClass: "json-data"` and `capabilities: ["json-data"]`, and must explicitly declare no file transfer or GUI requirement. A declaration describes a workflow; it does not add an adapter for its capabilities.
- Inputs and outputs use bounded JSON. File/binary transfer, runtime object adaptation, desktop/UI work and arbitrary local paths are unsupported in this capability. The current limits are 1 MiB encoded JSON, depth 12, 200 object properties, 1,000 array items and 100,000 characters per string. The server profile is authoritative; the node rejects a mismatched limit contract.

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

### JSON data workflow boundary

Use **Get Workflow** before execution and verify `profile.capabilityClass` is `json-data`, `profile.admission.allowed` is `true`, and the returned `inputSchema` matches the data being sent. JSON values preserve `0`, `false`, `null`, arrays and nested objects. Unknown fields, non-finite numbers, runtime objects, file values and values over the published limits are rejected before dispatch.

The result remains one JSON value under `result`; arrays are not expanded into n8n items. An optional declared `outputSchema` documents the result shape, but it does not enable file, GUI or runtime-object capabilities. Other RPA capability classes are outside this release's node contract.

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
