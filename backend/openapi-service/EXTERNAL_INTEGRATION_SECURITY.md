# External integration security contract

AstronRPA exposes common service capabilities over MCP Streamable HTTP and REST.
MCP is the primary discovery/execution/query channel; REST is auxiliary and an
explicit compatibility interface. Neither an authentication failure nor an
uncertain start response permits retrying a start over another transport.

## Identity and trust boundary

External calls authenticate with exactly one `Authorization: Bearer <API_KEY>`
or `X-API-Key: <API_KEY>` header. Both transports use the same active-key lookup
and bcrypt verification. Duplicate/conflicting headers, malformed credentials,
invalid/revoked keys and REST `?key=` credentials return HTTP 401. MCP URL keys
remain disabled by default; `MCP_ALLOW_QUERY_API_KEY=true` is a temporary MCP-only
migration option, not a production recommendation. Authentication store failures
return HTTP 503 without database details. Keys are rechecked on every request;
there is no positive authentication cache that survives revocation.

Desktop key management and workflow publication use the existing authenticated
session gateway. The OpenAPI gateway strips incoming `user_id`, `X-User-Id` and
`user-info` before authentication. Only the identity obtained from the existing
robot/auth service is forwarded. API-key requests cannot use management routes
or impersonate a desktop WebSocket connection. Hybrid workflow reads use API-key
identity whenever an API credential is supplied; they never fall back after an
invalid credential. Session-only reads retain the designer's existing view.

The OpenAPI container port must remain **private**, as in the supplied Compose
file. Internal robot-service publication requests still assert `user_id` on the
trusted service network. Direct public exposure of that port or a replacement
proxy that forwards caller-supplied identity headers breaks this trust boundary.
Upgrade the OpenAPI application and its gateway policy together.

OpenAPI keys, workflows and executions currently bind to `user_id`, not to a
verified tenant context. Session authentication supplies an existing identity;
OpenAPI does not implement a second account system. Use separate identities and
deployments for test/production and for tenant isolation. A shared deployment
requiring the same user to have different tenant grants is not supported by this
contract. Supplying tenant/user IDs in request data does not establish a grant.

## Current authorization matrix

| Entry point | Identity | Enforced resource permission |
| --- | --- | --- |
| Fixed MCP list/get | API key | Owner, external access enabled, valid published version; fixed tools require exact projectId |
| Dynamic MCP discovery/call | API key | Same owner/open-release policy; startup rechecks the version resolved during discovery |
| Fixed MCP / REST start | API key | Authorized project/current version and enrolled-scope admission before record creation or dispatch; executor only; no delegated phone identity |
| MCP execution get/cancel / REST execution list/get | API key | Execution owner and current workflow owner, enabled external access and a valid accepted execution version |
| REST workflow list/get with API key | API key | Current owner's open, published workflows; legacy example alias may resolve only to that owner's authorized copy |
| Key create/list/revoke, workflow upsert, Astron credential management | Authenticated desktop session through the private gateway | Current user; API keys cannot mint keys or grant external workflow access |
| `/workflows/stop-current` | API key | Targets the authenticated user's client only; no caller-selected target identity |
| `/health/remote-check` | API key | Reports only that user's client presence; does not start work |
| `/health/local-check` | API key | Compares a diagnostic client identity; the supplied comparison value does not authorize access |
| `/users/register`, `/users/get-key`, cross-user copy/delegated start | Disabled | Historical shared tokens/phone lookups do not prove a delegation grant |

Ordinary republication preserves access to already accepted execution records.
External-access revocation, workflow deletion or ownership changes deny access,
including through REST list counts; API key revocation denies requests. These
changes do not stop an already accepted task. Missing and invisible resources
have equivalent denial behavior. REST start uses 404 for unavailable projects and 403 for a disallowed
version or execution mode. Execution detail uses 404. Workflow detail preserves
its existing response envelope with no data for an unavailable resource. MCP
tool denials use `isError`/safe business errors, not HTTP authorization statuses.

API keys currently have **user-level permission**, no per-key scopes or expiry
field. An owner explicitly enabling external access grants execution of that
release to that owner's keys. Reading workflow metadata is not the same as
executing a workflow that happens to perform read-only business work. MCP tool
annotations and n8n node filtering do not constrain server-side authorization.

## Workflow capability boundaries

| Capability | Integration requirement |
| --- | --- |
| Metadata read | Authenticated owner and allowed workflow; no execution as a connection test |
| Read-only business workflow | Explicitly enabled release, controlled inputs and external credentials |
| External write | Separate reviewed workflow/identity; recover uncertain starts with the original stable business key |
| Files / Office | Authorized file handles, access limits and lifetime policy; no arbitrary local paths |
| Desktop / UI | Authorized executor, session readiness and real stop confirmation |
| AI automatic invocation | Allowed tools/inputs and independent authorization; model output is not a grant |
| High-risk/irreversible work | Reviewed allowlist and human approval or prohibition of automatic invocation |

These are admission requirements, not newly implemented per-key capability
scopes. Administrator-owned declarations apply additional admission checks to
enrolled users across fixed MCP, dynamic MCP and REST. Supported JSON and declared
secret inputs follow the [execution management contract](EXECUTION_MANAGEMENT.md);
file and runtime objects remain unsupported. Operators must publish only workflows
they intend to allow the integration identity to execute.

## Key lifecycle and migration

Create a key through the signed-in desktop settings. Only the creation response
returns the new raw key; `openapi_auth` stores its hash and prefix. Subsequent key
lists return masks. Keep the raw key in the caller's credential store, never in
a workflow's JSON, URL, source code or exported example.

Rotate without starting a task:

1. Create a new key for the intended identity/environment.
2. Initialize MCP and discover/read authorized workflows with the new Credential.
3. Switch callers to the new Credential. An empty authorized workflow list is a
   successful authentication result, not a reason to execute a task.
4. Revoke the old key through its owner's session. Subsequent MCP/REST requests,
   including requests on an existing HTTP connection, must reject it.

Keep the overlap short. If verification fails before revocation, retain the old
Credential while fixing configuration. A revoked key is not reactivated by this
flow: create another key if necessary. Revocation prevents new requests but is
not execution cancellation. Without automatic expiry, operators schedule
rotation and revoke unused/compromised keys explicitly.

Compatibility changes to review before deployment:

- API keys cannot access session management endpoints or authenticate WebSockets.
- Raw public user headers and invalid-Bearer fallback are removed at the gateway.
- REST starts can no longer select disabled/unpublished/different releases,
  editor execution or another user's phone. Unknown top-level execution fields
  are rejected; use `params` for business inputs.
- Legacy shared-token phone key provisioning and cross-user copy return denials.
  Use authenticated key management; delegated execution is unsupported.
- Existing external callers retain access to accepted executions after ordinary
  republication. Revoking access still denies reads and cancellation; retaining
  an execution ID does not establish authorization.
- Legacy user provisioning may have stored plaintext `default_api_key` values in
  historical user records. This change blocks that public provisioning path; it
  does not rewrite existing database rows or backups. Inventory affected keys,
  rotate/revoke them, and remove obsolete plaintext copies under the deployment's
  data-retention policy. No automatic destructive data migration is performed.

Per-key scopes, automatic expiration, shared-tenant authorization and delegated
identities are not provided by this contract.

## n8n Credentials

| Field | Contract |
| --- | --- |
| MCP Endpoint | Full deployment-supplied HTTPS URL including its configured path; do not guess or discard path segments |
| API Key | Secret credential field; standard Bearer header, never query data |
| Protocol | MCP `2025-11-25` over Streamable HTTP; no automatic protocol upgrade/fallback |

Use normal certificate-chain/hostname validation. Loopback/tunnel transport is
only a development test environment, not a Community Node requirement. The
[AstronRPA community node](../../integrations/n8n/n8n-nodes-astron-rpa/README.md)
provides the Credentials UI and uses MCP for all business operations. Its n8n SDK
dependency is confined to the independent node package.

Connection testing may initialize MCP, discover tools and perform an authorized
read. It must not call execute/stop, use REST fallback starts, or auto-retry a
start. Distinguish invalid/revoked key, TLS/network failure, protocol mismatch,
discovery-service failure and authenticated identity with no visible workflows.
n8n workflows retain only a Credential reference. Instance encryption keys,
credential sharing and encrypted backups belong to the n8n administrator.

## Deployment and acceptance

Follow [HTTPS deployment](../../docker/HTTPS_DEPLOYMENT.md). Deployers supply and
maintain servers, DNS, certificates/private keys and renewals. Application
configuration, images and documentation are provided by the project; neither
shared developer certificates nor SSH tunnels are production dependencies.

Casdoor generates independent signing keys and application secrets on first
initialization and preserves them on restart. The deployment synchronization
command copies only the selected application's Secret and public signing
certificate into its ignored `.env`. Deployments initialized from earlier
public bootstrap keys need an explicit key/Secret rotation and default-account
review; updating the JSON or the gateway TLS certificate cannot do this.
See the HTTPS guide's authentication initialization/rotation section.

Back up the project deployment's configuration and record the application image
and source version before switching. Keep the client idle, deploy the gateway
policy and application together, validate the rendered nginx configuration and
reload only this project's gateway. Check login, Secure cookies, WSS and MCP
POST/SSE with buffering disabled. After certificate replacement/renewal, repeat
trust/hostname checks and reconnect the client/MCP caller. Roll back using the
project's saved configuration/image; do not alter host-wide proxy/certificate
configuration or unrelated services. Reverting security code also restores its
old exposure and requires isolating external access during rollback.

Update the desktop client as well: its Chromium process must use normal
certificate validation, without the historical global certificate-error bypass.
The Scheduler's remote transport owns verified HTTPS/WSS connections; the
bundled local router connects to that transport over loopback and continues to
route local modules. Do not run that binary as a standalone remote TLS client:
its historical transport skips certificate verification. The configured public
`remote_addr` remains the deployment's URL, without requiring an SSH tunnel.
Sessions are persisted per configured origin under `.remote-cookies` in the
client working directory. Only that origin's existing session is migrated from
`.cookie.json`; upstream cookies are not delegated to the binary's temporary
loopback identity. Logout clears the new store, including across restarts.
Malformed local session data is discarded without logging its contents, so a
fresh login remains possible; a damaged new store does not restore old legacy
credentials. Both session-store paths are excluded from Git.
HTTP and WSS requests do not automatically follow redirects with session
credentials. Configure the final deployment endpoint explicitly.
HTTPS gateway listeners add Secure/HttpOnly to the Casdoor session cookie,
including the gateway's Casdoor proxy path; explicit legacy HTTP listeners keep
their existing cookie behavior.

The OpenAPI WebSocket manager binds each received message to its own handler,
including buffered busy/success replies. This is a compatibility fix for the
bundled `rpawebsocket` 1.0.7 listener; it preserves the existing wire protocol
and does not implement persistent execution recovery after a service restart.

Unit/ASGI tests and isolated OpenResty tests do not constitute production TLS
acceptance. Deployment validation requires trusted HTTPS/WSS with the actual
deployment domain, wrong/expired certificate rejection, real n8n/desktop success,
business failure, offline/busy and timeout/same-ID continuation, redaction checks
and certificate replacement/recovery. Record unavailable conditions as untested.

Review gateway/service/client logs and n8n history for credentials and internal
error data. Legitimate workflow results may contain business secrets: restrict
history access, retention and exports. Managed execution extends this security
contract with durable idempotency, reconciliation and confirmed cancellation;
see [execution management](EXECUTION_MANAGEMENT.md). Cancellation uses the same
execution ownership and current workflow ownership/external-access checks. Legacy
Clients retain `supportsCancel=false`; revoking a Key still does not cancel running work.
