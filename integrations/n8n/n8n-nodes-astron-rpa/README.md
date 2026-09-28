# AstronRPA community node (development)

Control published AstronRPA workflows through authenticated HTTPS MCP: discover workflows, start an execution, wait for its result, query its state and request cancellation.

## Scope and requirements

- This development package provides the common execution framework for individually approved workflows with `supportScope: controlled-validation`. An approved workflow does not establish support for an entire RPA capability family.
- The verified host configuration is self-hosted n8n `2.36.9`, Node.js `24+`, one OpenAPI connection owner and one Windows client matching the repository, with managed client protocol `1`. The package declares `n8n-workflow >=2.36.4 <3`; other host versions, queue mode, multiple replicas or terminals, n8n Cloud and older clients are not covered by this validation.
- OpenAPI must provide integration contract `1`, profile schema `1` and MCP `2025-11-25`. MCP is the primary channel. A published capability may explicitly allow the REST auxiliary transport; the node never switches transports after an uncertain start.
- Capability declarations include a stable `capabilityClass`, `capabilities`, `componentOperations` and `allowedTransports`. Current controlled validation includes `json-data` plus reviewed service/browser-read classes. A declaration describes a workflow; it does not add an adapter for unsupported Engine operations.
- Inputs and outputs use bounded JSON. File/binary transfer, runtime object adaptation, desktop/UI work and arbitrary local paths are unsupported in this capability. The current limits are 1 MiB encoded JSON, depth 12, 200 object properties, 1,000 array items and 100,000 characters per string. The server profile is authoritative; the node rejects a mismatched limit contract.

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

A workflow with secret inputs suppresses the entire RPA result: `resultVisibility: suppressed-for-secret-inputs` explains a null result. n8n's normal execution storage can still contain supplied inputs; apply its access and retention controls. Store API keys in credentials, not workflow inputs.

### Capability boundary

Use **Get Workflow** before execution and verify `profile.capabilityClass`, `profile.componentOperations`, `profile.allowedTransports` and `profile.admission.allowed`. The node does not infer a capability from a workflow name or component name. Browser, HTTP, database, mail and shared-service reads require a complete operation-level declaration. Mixed workflows must satisfy every applicable constraint; approval for one category never grants another. The reserved `service-openapi-read` identifier has no approved operations: current Engine OpenAPI operations require files and belong to the Office/file category.

Select **MCP (Primary)** unless the published declaration explicitly includes `rest` in `allowedTransports` and the operation has a documented REST auxiliary route. REST is never an automatic fallback for an uncertain MCP request.

Read workflows require `readContractVersion: 1` from an administrator-reviewed release. HTTP permits GET/HEAD without upload or save; mail preserves unread state and does not save attachments; browser extraction stays on one page without export; database SQL is fixed and reviewed with read-only credentials. The review is not a sandbox for arbitrary Python or SQL. Connection objects, element handles and generators remain inside the workflow, and results use the shared bounded JSON contract. REST submission, observation and cancellation preserve the server's execution identity, state and result visibility.

Browser reads require the intended active browser tab and the installed AstronRPA extension; reserve the terminal during execution. The SQLite read-only connection option is `connect_info.read_only: true`. MySQL uses the packaged driver; PostgreSQL, SQL Server, Access and Oracle require their corresponding optional database drivers. A successful SQLite test does not establish compatibility with those database deployments.

### JSON data workflow boundary

Use **Get Workflow** before execution and verify `profile.capabilityClass` is `json-data`, `profile.admission.allowed` is `true`, and the returned `inputSchema` matches the data being sent. JSON values preserve `0`, `false`, `null`, arrays and nested objects. Unknown fields, non-finite numbers, runtime objects, file values and values over the published limits are rejected before dispatch.

The result remains one JSON value under `result`; arrays are not expanded into n8n items. An optional declared `outputSchema` documents the result shape, but it does not enable file, GUI or runtime-object capabilities. Browser/service reads use their own peer capability module and declaration.

## Capability layout and plan mapping

Stage 4 consists of a common framework and five peer capability groups. Sections 4.1-4.5 in `Implement.md` specify delivery order, not inheritance or nesting. The node invokes published workflows through the common transport and execution framework; capability modules validate their declarations rather than calling Engine components directly.

```text
n8n-nodes-astron-rpa/
|-- credentials/                 # Shared credential handling
|-- nodes/                       # Shared n8n entry point
|-- transport/                  # MCP primary / explicit REST auxiliary
|-- execution/                  # Shared lifecycle, idempotency and recovery
|-- mapping/                    # Shared JSON values, snapshots and errors
|-- capabilities/
|   |-- json-data.ts             # 4.1-specific declaration checks
|   |-- browser-service.ts       # 4.2-specific declaration checks
|   `-- shared/
|       |-- types.ts             # Wire identifiers and profile types
|       |-- catalog.ts           # 25 components -> five peer plan groups
|       `-- registry.ts           # Dispatch to the matching capability module
|-- tests/
`-- examples/
```

`shared/catalog.ts` maps component operations to categories, not 25 components to 25 nodes or mutually exclusive categories. A component may span several groups. `CAPABILITY_GROUPS` records the exact plan section; group names describe source organization, while existing `capabilityClass` values remain unchanged on the wire.

| Plan | Peer group / module            | Component coverage by operation                                                                                           |
| ---- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| 4.1  | `json-data.ts`                 | dataprocess, datatable, encrypt, report, reviewed script                                                                  |
| 4.2  | `browser-service.ts`           | browser, network, database, email, enterprise reads                                                                       |
| 4.3  | `office-file.ts` (planned)     | datatable, browser, enterprise, excel, network, openapi, pdf, system, word file operations                                |
| 4.4  | `desktop-ui.ts` (planned)      | browser, cua, dialog, input, software, system, verifycode, vision, window, winelement interaction                         |
| 4.5  | `ai-dynamic-risk.ts` (planned) | ai, browser, cua, database, email, enterprise, network, script, smart, verifycode, vision dynamic or high-risk operations |

Future modules belong beside `json-data.ts` and `browser-service.ts`, use the shared registry and common framework, and do not import a previous category's implementation. Planned names are documentation only; no empty modules or unsupported handlers are registered. Catalog coverage is an inventory, not a claim that every listed operation has been implemented or verified. Shared utilities should stay neutral; server/client defects belong in their original modules.

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

## Repository documentation

- [Server admission configuration](../../../backend/openapi-service/README.md#integration-admission)
- [Example workflow](examples/README.md)
- [Validation results and incomplete checks](../VALIDATION.md)

These references are in the source repository. Validation procedures, environment details and execution evidence are maintained in the validation record.
