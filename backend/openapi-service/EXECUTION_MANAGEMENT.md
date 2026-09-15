# External execution management

MCP and REST use the same authorization, execution records and Client protocol.
This module contains no n8n workflow state or platform SDK. Platform adapters
must save `executionId` and use it to query or cancel the original execution.

## Tools and states

The fixed tools are `astron_workflow_list`, `astron_workflow_get`,
`astron_workflow_execute`, `astron_execution_get` and `astron_execution_cancel`.
Execute accepts `projectId`, optional `version`, `params`, `idempotencyKey` and
`executionTimeout` (1–86400 seconds). REST uses the corresponding snake_case
fields. Existing dynamic tools retain their synchronous result envelope.

| State | Evidence |
| --- | --- |
| `accepted` | Server execution receipt committed; Client may still be preparing |
| `running` | Bound Client confirms the actual Executor process started |
| `succeeded` / `failed` | Bound execution result, or a definite rejection before start |
| `cancelled` | Client confirms zero launch or stopping the exact process |
| `timeout` | Execution deadline triggered and stopping the exact process is confirmed |
| `unknown` | Observation is incomplete; the process may still be running |

Confirmed terminal states are immutable. Responses include the published version,
Client/run association, UTC accepted/started/finished timestamps, result and safe
error. Historical records without the managed Client protocol retain their old
capability limitations; a legacy database cancellation is reported as `unknown`.

`cancelRequested=true` records intent, not completion. Cancel rechecks ownership
and current resource/version authorization. The command targets the bound Client
and run, never the user's next task or `stop_current`. Completion racing with
cancel keeps a confirmed success. Unsupported Clients reject cancellation rather
than changing the record to cancelled.

Three timeouts have different effects:

- MCP request timeout/disconnect ends that request only.
- A caller's polling budget ends its wait; keep the execution ID for later queries.
- `executionTimeout` starts when the actual Executor process launches. The Client
  requests its stop at the deadline and reports timeout only after stop evidence.

Stopping an Executor cannot undo completed business actions or promise that an
external application has reverted its own work. A failed stop stays unconfirmed:
after a stop error or ten seconds without process exit, the snapshot reports
`unknown` / `STOP_UNCONFIRMED` and continues observing for a real late outcome.

## Idempotency and recovery

Use a new opaque idempotency key for each intended execution. Reusing the same key
and request under the same authenticated user returns the original ID; different
inputs return `IDEMPOTENCY_CONFLICT`. Canonical comparison sorts JSON object keys
and includes the caller's version selection and execution options. Omitted and
explicit versions/options are different requests. The first resolved publication
and defaults are frozen. Each retry still checks current authorization; if the
publication is no longer externally accessible, the old execution is not exposed.

The database unique constraint applies across concurrent requests and restarts.
Only a `NEW` dispatch receipt can atomically become `SENT` and send a start. A
claimed dispatch, including a crash immediately before sending, is only queried
after recovery. It is never automatically reissued. The Client also commits a
receipt before launching and deduplicates the stable execution identity.

New dispatches expire after 30 seconds if they have not been claimed. Busy/offline
rejections are not queued. Results that cannot be reconciled remain unknown.
Do not create another ID or fall back to a REST start to recover an uncertain task.
This is duplicate prevention and reconciliation, not exactly-once desktop effects.

The Scheduler stores receipts in its runtime `.executions/` directory, separated
by deployment origin and authenticated user. Engine terminal receipts allow a
restarted Scheduler to recover late results. Recovery checks run identity and the
original process identity before accepting a saved terminal receipt. Restart does
not resume GUI execution or reissue a task. Existing Client startup cleanup can
stop leftover processes; without a terminal receipt their outcome stays unknown.
Execution deadlines cannot be guaranteed while the Scheduler itself is down.
New external starts are refused while a retained, unresolved run may still be
alive. A crash between binding the run and saving its process identity requires
operator reconciliation before reopening external starts; do not delete receipts
to trigger a retry.

Keep execution/idempotency receipts and Client journals for the deployment's
lifetime. There is no automatic expiry or key reuse window. Workflow deletion
preserves execution history; external access still requires an authorized current
workflow. Do not purge these identities as a routine log cleanup. If an operator
resets the database or journal, fence old callers and rotate the integration Key
before accepting new work; retries from the old deployment have no guarantee.

The existing WebSocket ownership model requires one OpenAPI worker/replica per
deployment. Database arbitration is durable, but this change does not introduce
distributed WebSocket routing or a multi-Client scheduler. Only the current
connection receives a command; replies from other/older connections are ignored.

## JSON inputs and sensitive values

Published inputs support string, integer, finite number, boolean, array, object,
enum, date and timezone-qualified date-time. Date-time requires seconds and an
explicit `Z`/numeric offset; leap seconds are not accepted. Nullable fields must
declare null support. Defaults are applied once; caller values are not coerced.
Managed Client inputs are JSON literals and never enter expression evaluation.
File/binary values, remote schema references and runtime objects are unsupported.
Legacy Clients without the managed protocol may receive only the original scalar
inputs; rich JSON and declared secrets require an upgraded, connected Client.

For a new request requiring managed execution (idempotency, an execution deadline,
rich JSON or secrets), a missing/disconnected Client returns `CLIENT_OFFLINE`.
A failed or timed-out capability probe returns `CLIENT_CAPABILITY_UNCONFIRMED`;
it is not evidence that the Client needs upgrading. A reply without the managed
protocol returns `CLIENT_PROTOCOL_UNSUPPORTED`. These rejections create no
execution and dispatch no task. Fixed MCP tools return these codes as tool errors;
both REST start routes return `detail.code` and a safe `detail.message`, with HTTP
503 for offline or unconfirmed capabilities and HTTP 409 for unsupported protocol.
Discovery still works while offline, and an authorized repeat of an existing
idempotent request returns its original ID
without requiring a live Client. Do not automatically retry an uncertain start
or switch to REST; retain the same key and execution identity.

Password/write-only defaults and enums are omitted from discovery. Inputs needed
for the initial dispatch remain in the existing restricted execution storage;
this is not a new encryption or secret-management system. Idempotency stores
hashes rather than another input copy. Public REST masks declared secret inputs,
and managed terminal handling replaces their stored values with redaction markers.
Client receipt journals do not store input payloads. Existing parameter temp files
and robot execution history remain deployment data and require restricted access
and an appropriate retention policy.

For workflows declaring secret inputs/outputs, public result summaries and Engine
diagnostic payloads are omitted conservatively. User-authored workflow actions
must still handle sensitive data appropriately; this does not make arbitrary
business output public or sanitize external applications' own logs.

## MCP compatibility

The legacy binding uses pinned Python MCP SDK `1.26.0` for `2025-06-18` and
`2025-11-25` initialization, version headers and request SSE responses. The same
endpoint also handles `2026-07-28` through a request-scoped binding:

- No initialize handshake, protocol session or GET stream. `server/discover`,
  `ping`, `tools/list` and `tools/call` are supported; only tools are advertised.
- Each request requires matching `MCP-Protocol-Version`, `Mcp-Method` and,
  for tool calls, `Mcp-Name`, plus per-request protocol/client-capability metadata.
- Header mismatches return HTTP 400 / `-32020`; unsupported versions return
  HTTP 400 / `-32022`; unknown methods return HTTP 404 / `-32601`.
- Modern responses use JSON. Clients must accept both JSON and SSE as required
  by Streamable HTTP. Sessions and `Last-Event-ID` are not minted or resumed.
- API authentication remains mandatory. Browser Origins are denied by default;
  deployers may explicitly configure comma-separated `MCP_ALLOWED_ORIGINS`.

No change to an SDK flag is treated as proof of a new protocol version. Target
platforms must use a protocol revision supported by their actual MCP client.

## Upgrade and rollback

1. Stop new external starts and verify Client idleness. Back up the deployment
   database, OpenAPI source/image and Client runtime under your own project paths.
2. Stop OpenAPI. For an existing database, apply
   `migrations/001_execution_management.sql` once in the RPA database. It adds
   nullable legacy-compatible columns, the user/key unique constraint, and removes
   cascading workflow deletion. New installs use `docker/volumes/mysql/schema.sql`.
3. Upgrade Scheduler and Executor together, then OpenAPI. Preserve runtime
   cookies, execution journals and Engine terminal receipts. Verify HTTPS/WSS,
   tool discovery, `supportsCancel` and a disposable workflow before reopening.
4. To roll back, quiesce starts and reconcile/cancel active managed executions
   first. Keep the expanded schema and retained receipts. An old Server/Client
   cannot provide managed recovery, idempotency or confirmed cancellation; do not
   enable automated retries while rolled back. Restore the matching version pair
   to resume observation. Never restore a stale database over newer execution IDs
   while callers can still retry them.

Domain, certificates, private keys and ports remain deployer configuration. See
[`docker/HTTPS_DEPLOYMENT.md`](../../docker/HTTPS_DEPLOYMENT.md) and
[`EXTERNAL_INTEGRATION_SECURITY.md`](EXTERNAL_INTEGRATION_SECURITY.md).
The independent Community Node and complete Client installer are stage 4 work.
