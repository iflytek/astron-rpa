# Self-hosted operations

This guide covers the community node's deployment, execution control and package maintenance. Capability admission is configured per published workflow and approved version. Dated test results and pending environment checks are in [VALIDATION.md](VALIDATION.md).

## Install and upgrade

1. Pin the n8n runtime and node tarball using the [compatibility matrix](COMPATIBILITY.md). Check `node --version` in **every executing host/container** (Node 24 or newer), and record `n8n --version`. For a source build, follow the package checks below; for a published version, retain its version and integrity.
2. Back up the n8n database and encryption key together, the OpenAPI database, private integration policy and file store. Do not export decrypted credentials into a repository or support log.
3. Follow OpenAPI's [upgrade and rollback steps](../../backend/openapi-service/EXECUTION_MANAGEMENT.md#upgrade-and-rollback), including all required migrations, before replacing application code. Startup checks reject missing execution columns before accepting traffic. Preserve execution records, idempotency keys, client receipts and policy revisions.
4. Pause new triggers, let active work reach a known state, install the **same tarball** on the n8n main process and every worker, and restart them. A running process does not reload a replaced node package. Compare the installed `dist` hashes with the built tarball.
5. Test discovery, one approved synthetic execution, query, precise cancellation and a persisted wait across restart. For rollback, restore a compatible application/package version; do not downgrade the database or erase receipts to force a retry. An uncertain execution is queried by its existing ID/key.

For a full Windows Client package, set the deployment's HTTPS origin in the build copy of `resources/conf.yaml` before packaging, and verify the installed `resources/conf.yaml` before starting the Client. The repository's loopback address is a default, not the address of a remote deployment. Keep the previous program and configuration together for rollback; an installer can replace the installed configuration. Keep deployment-specific hostnames outside the shared source defaults. Verify the configured gateway and authentication endpoints, login, Client readiness and an actual synthetic execution after installation.

## Build and release

Run package commands in `integrations/n8n/n8n-nodes-astron-rpa`. Capability validators are peer modules under `capabilities/`; `shared/` holds their common types, catalog and dispatch. Credentials, transports and execution lifecycle are shared. Changes to one category should not duplicate lifecycle code or imply admission of other operations. Server/Engine fixes belong in their owning modules and need their own regressions.

`npm run release:check` runs type checking, ESLint, formatting, node tests/build, the production dependency audit and the package-consumer test, followed by a full audit including development dependencies. Both audits fail at moderate or higher severity; a registry/network error also fails the check. A clean production audit alone does not pass the release gate. The consumer test installs the tarball independently and exercises its bundled SDK. The repository [integration workflow](../../.github/workflows/integration-regression.yml) also runs the targeted OpenAPI, isolated Engine and AI suites. Keep reports, tarballs, temporary credentials and live fixtures outside the source tree. These checks complement the host-specific acceptance in [VALIDATION.md](VALIDATION.md).

### First manual publication

The public package is `@iflytekopensource/n8n-nodes-astron-rpa`; its node-panel name is **Astron-RPA**. The initial scoped version `0.1.0` is prepared for manual publication. Pushing a branch or merging a PR does not publish it. The [publish workflow](../../.github/workflows/publish-n8n.yml) runs regression for `n8n-v<version>` tags but skips publication for `n8n-v0.1.0`. Later version tags require the tagged commit to be on `main` and all integration regression jobs to pass. The workflow checks the package/tag/repository identity, audits the full release dependency tree and publishes the saved tarball with npm provenance. A failing audit or regression prevents publication.

For the first release, run these commands from the node package directory using Node 24 and an npm account authorised to publish in `iflytekopensource`. Keep the output directory outside the repository. Complete host acceptance and resolve failing dependency gates before publication. The PowerShell guard below stops the procedure when checks fail:

```powershell
npm ci
npm run release:check
if ($LASTEXITCODE -ne 0) { throw 'Release checks failed; do not publish.' }
$releaseDir = Join-Path $env:LOCALAPPDATA 'astron-rpa-releases/0.1.0'
New-Item -ItemType Directory -Force -Path $releaseDir
npm pack --pack-destination $releaseDir
$releaseFile = Join-Path $releaseDir 'iflytekopensource-n8n-nodes-astron-rpa-0.1.0.tgz'
Get-FileHash -Algorithm SHA256 -LiteralPath $releaseFile
npm publish $releaseFile --dry-run --access public --tag latest
```

`--dry-run` checks the publication contents without uploading them. Install and test this exact tarball, retain its SHA-256, and ensure the intended source commit is reviewed before publication. When the maintainer is ready, authenticate with `npm login --registry=https://registry.npmjs.org/` (including MFA as requested), verify the account with `npm whoami`, and execute `npm publish $releaseFile --access public --tag latest`. Publish the accepted tarball. If any files change, rebuild it and record the new hash, changed files and applicable checks. Verify the published version and integrity with `npm view @iflytekopensource/n8n-nodes-astron-rpa@0.1.0 version dist.integrity`, then install that version on a clean supported host.

### Subsequent automated publication

Before enabling automatic publication for later versions, an npm organisation member with package-publish permission must configure the repository's `npm` GitHub Environment with release reviewers and tag restrictions. After the manual first publication, configure npm Trusted Publishing for the actual publishing GitHub repository, workflow filename `publish-n8n.yml`, and environment `npm`. Use a current Node 24/npm toolchain with OIDC support. A short-lived, package-scoped granular token in the environment secret `NPM_TOKEN` is an alternative if Trusted Publishing is unavailable; remove it once OIDC is enabled. These GitHub settings are not prerequisites for the manual first release. Do not store tokens in source or workflow inputs. The package's `repository` metadata must match the publishing repository for provenance.

Before tagging, update the package and lockfile version, complete acceptance for the supported host/software combinations, review the full dependency audit (including the n8n host), resolve automated gate failures and obtain maintainer review of remaining host-acceptance limits. A failed publish must be investigated; an already published version cannot be overwritten. Confirm npm version/integrity/provenance and install that exact version on a clean supported host before rollout.

## Dependency maintenance

The release tarball includes compiled runtime JavaScript, package metadata, the user README/license, three importable example workflows and their instructions, plus the bundled MCP SDK runtime dependency tree and its upstream licenses. The packaged README retains installation and user configuration instructions: n8n credentials, server admission, client prerequisites, file storage and workflow settings. `dist/package.json` provides the SDK client identity at runtime. Project type declarations, TypeScript source, tests, CI/build configuration, test-environment fixtures, private deployment-instance configuration and local credentials are excluded. Server/container deployment manifests and their detailed administration guides remain in the repository, linked from the packaged README. Upstream dependencies retain the files and licenses distributed by their publishers. `VALIDATION.md`, `validation-evidence.json`, `COMPATIBILITY.md` and this operations guide remain repository documentation; excluding those files does not exclude the user configuration instructions in the README and examples.

The package `files` allowlist selects the published paths. `npm run test:package` checks the complete packed project-file list against the runtime source modules and explicit user files, checks that examples are inactive and have no credential bindings, then verifies a clean consumer installation. A new example or runtime asset must be deliberately added to the release list and package check.

The tarball bundles the MCP SDK and its audited runtime dependencies from `npm ci`, including the SDK's own Zod 4 dependency. This preserves the tested runtime tree when consumers install the package; a root-only npm override would not constrain a consumer's dependency resolution. Keep the SDK override and lockfile current, run `npm run test:package`, and inspect a clean tarball installation after dependency changes. Bundling increases artifact size and requires a new package release for dependency fixes. The n8n host and the development `n8n-workflow` fixture have their own dependencies and must be audited separately; do not force the host onto a different Zod major through a global override.

The development `n8n-workflow` fixture uses a scoped Axios 1.x override; it does not change the installed n8n host. Local `release:check` and automatic publication retain strict full audits with no advisory exceptions. Run this gate explicitly with `npm audit --include=dev --audit-level=moderate`; do not use `npm audit fix --force` or an incompatible major override to clear its output.

Integration regression CI keeps its strict production audit and evaluates the full report with [check-n8n-audit.cjs](../../.github/scripts/check-n8n-audit.cjs). Until the end of 2026-11-10 UTC, it permits only the existing `GHSA-mrhx-c7xc-m3w5` chain through development-only `n8n-workflow@2.36.4`, `@n8n/expression-runtime@0.27.1` and `zod@3.25.76`, at their exact reviewed lockfile paths. This lets isolated synthetic regression continue while a compatible upstream patch is unavailable. The raw report remains an artifact and the job emits a warning. Changed findings, versions or paths, production scope, expiry, malformed reports and audit process/network errors fail the job; there is no blanket `continue-on-error` or ignored exit status. This exception does not apply to release checks or the installed host, and does not authorise publication. Keep synthetic inputs bounded and deployment credentials out of regression jobs; bbdu3 should revisit the exception before expiry and remove it after a compatible upstream repair passes regression and full audits.

Audit the installed n8n distribution and its community-nodes directory separately. Production-only package audit success excludes both trees. For an installation without a root lockfile, collect the actual installed package names, exact versions, locations and dependency edges with npm Arborist `loadActual`, export an audit-only lock snapshot outside the installation, and run `npm audit --omit=dev --json` there. Do not install or resolve package ranges in that snapshot: doing so would audit a different tree. Keep the inventory/report hashes and date with the validation evidence. Audit counts include parent packages affected through dependencies and do not establish exploitability. A snapshot's `fixAvailable` suggestions do not prove that an upgrade clears all findings.

Prioritise critical/high host findings, select a maintained compatible n8n distribution, and test it in isolation before replacing main/workers. Upgrade community packages and their shared peers through the supported installation procedure; do not patch arbitrary nested `node_modules` or apply a global Zod override. Repeat both host audits and the installation, execution, waiting/recovery and queue checks before rollout. Record any remaining findings and the deployment maintainer's decision; the community node's bundled SDK and smoke tests do not patch the host. The latest audit status and assigned follow-up are in [VALIDATION.md](VALIDATION.md).

## Installation and discovery

After npm publication, install `@iflytekopensource/n8n-nodes-astron-rpa` through Community Nodes in a self-hosted n8n deployment with community package installation enabled. After installation, search for **Astron-RPA** in the node panel. The package includes the `n8n-community-node-package` discovery keyword and RPA, data, browser, Office, desktop and AI automation keywords.

## Queue mode

Use a separate PostgreSQL database and private Redis instance/namespace, with the same database configuration and `N8N_ENCRYPTION_KEY` on main and workers. Do not use SQLite for queue deployment. The tested n8n `2.40.7` recommends PostgreSQL 17 or newer and warns that PostgreSQL 15 is unsupported. Configure `EXECUTIONS_MODE=queue`, `DB_TYPE=postgresdb`, `DB_POSTGRESDB_*`, `QUEUE_BULL_REDIS_*`, and `OFFLOAD_MANUAL_EXECUTIONS_TO_WORKERS=true`. Start the main process with `n8n start`. For workers, follow the host's concurrency guidance (`n8n worker --concurrency=5` is its recommended minimum), then measure your workload. Worker concurrency does not increase the Client's one-execution capacity; acceptance-fixture settings are not production sizing recommendations.

Install the community package on **all** processes. Set the public `N8N_WEBHOOK_URL` (the current n8n setting; older releases use `WEBHOOK_URL`), appropriate `N8N_PROXY_HOPS`, and the same encryption key. Main/workers must reach PostgreSQL, Redis, the resume webhook and AstronRPA HTTPS. Keep execution pruning enabled and retain unresolved wait checkpoints. The node's timer is only a latency optimization: n8n's persisted `waitTill` recovers waits after a process restart. The parent execution ID is preserved in the child request and sent on subsequent polls.

Restart recovery applies to a persisted waiting checkpoint. If the process is killed after the checkpoint has resumed into a running step, n8n can mark that child execution as crashed and leave its parent waiting. Query the original AstronRPA execution before resolving the n8n execution; use the original business key for an explicit replay after checking its receipt. Do not treat an interrupted n8n poll as proof that the RPA task failed or start it with a new key.

For Binary Data, use a storage mode supported by your n8n edition in queue mode and accessible to the executing workers. Validate upload/download on each worker host. The tested n8n 2.40.7 queue topology used `default` mode: inline Binary Data persisted within execution data in PostgreSQL. Filesystem or external object storage configurations require their own transfer and worker-access checks. Configure n8n Binary Data storage separately from AstronRPA file-handle storage.

## OpenAPI routing and persistent state

`EXECUTION_ROUTING=local` preserves single-process routing. To run multiple OpenAPI workers/replicas for managed protocol-1 workflows, set `EXECUTION_ROUTING=redis` on **every replica**, use the same authenticated private `REDIS_URL`, database, policy and persistent file store. A mixed local/Redis deployment is unsupported. Legacy clients without execution-management protocol 1 require the single-process configuration.

Redis routes authenticated owners to the process holding the current Client connection. A 30-second lease is renewed every 5 seconds. Replacement connections supersede old generations; expired or superseded local connections are closed. Commands and replies use transient pub/sub, not a durable command queue. Missing replies remain unconfirmed; Redis recovery never replays a start. The existing SQL `NEW -> SENT` claim remains the authority for one permitted dispatch. Redis unavailability fails closed and readiness returns 503.

For Compose replicas, remove/override the `openapi-service` fixed `container_name`, keep one Uvicorn worker per container, and reload the private upstream after changing replica addresses. Do not expose the OpenAPI port directly: trusted `user_id` headers require the existing authenticating gateway. API-key hashing is not a valid sticky-routing key because Client sessions use a different credential.

The current file store uses SQLite metadata plus local files. Replicas on one host must mount the **same** `INTEGRATION_FILE_ROOT` with working SQLite locks. Separate per-container stores and multi-host network filesystems are not supported by this topology. Each replica also needs the same private reviewed policy and output transfer URL. Runtime execution receipts are durable in the server database and Client store; ephemeral routing metadata is not a backup.

## Network, TLS and proxy checks

- Use a trusted HTTPS endpoint ending in `/mcp/`; validate hostname, chain and expiry from each n8n worker and the Windows Client. Configure TLS termination before installing HTTP-only deployments. Do not disable certificate checks.
- Allow only required destinations: n8n to AstronRPA HTTPS, queue workers to private PostgreSQL/Redis and the resume webhook, Client to its configured server/transfer endpoints, and service processes to their existing private dependencies. No inbound desktop port or SSH tunnel is needed for normal execution.
- Preserve POST bodies, `Authorization`, `Accept`, `Content-Type`, `MCP-Protocol-Version`, `Mcp-Method`, `Mcp-Name` and correlation headers. Disable MCP response/request buffering and proxy-level upstream replay. Request-scoped SSE must flush incrementally and end with the request; do not rely on a persistent subscription.
- The node uses MCP `2025-11-25`. The server also accepts legacy `2025-03-26`/`2025-06-18` and its `2026-07-28` no-session adapter. Test these **through the proxy**: initialize/tools/list/tools/call for legacy, metadata/header consistency and no `Mcp-Session-Id` for the modern adapter. Modern initialize, session resume and subscriptions are deliberately unsupported.
- Start the Windows Client through the desktop application in its interactive session. Verify login, Scheduler readiness, proxy settings and access to the configured HTTPS host. GUI workflows still require their declared display/session/software contract.
- Synchronize host clocks. Log timestamps are UTC, execution deadlines use UTC, and n8n workflow scheduling uses its configured timezone. Check Windows time, container UTC and the desired n8n `GENERIC_TIMEZONE`/`TZ`; do not change host timezone merely to make timestamps look equal.

## Logs, metrics and alerts

The optional [`docker-compose.integration-ops.yml`](../../docker/docker-compose.integration-ops.yml) overlay keeps the operations configuration persistent. Add it to the deployment's existing Compose file list; do not replace that list. Create a private `docker/.integration-ops.env` with `MONITORING_TOKEN`, `EXECUTION_ROUTING`, `INTEGRATION_RATE_PER_MINUTE` and `ASTRON_PROMETHEUS_IMAGE` pinned to an immutable image digest. Keep the same monitoring token in `docker/monitoring/secrets/openapi-token`, readable by the Prometheus container user only. Both secret locations are ignored by Git. Supply the environment file to Compose as well as to the service, and enable profile `integration-monitoring`.

The included single-process scrape configuration targets `openapi-service:8020`; replicas need one target per process. Persistent metrics storage is `docker/data/integration-monitoring` (container UID 65534), with 7-day/512-MB retention. The UI binds only `127.0.0.1:19090`, and the service restarts unless explicitly stopped. Before rollout run Compose configuration validation and `promtool check config`; afterwards check target health, `up`, `astron_ready`, loaded rules and port binding. Connect alert notifications only to a receiver approved by the deployment operator; the sample does not configure or send external notifications.

`LOG_FORMAT=json` emits structured UTC logs. `LOG_FORMAT=text` retains the traditional format. Correlation is diagnostic only: `trace_id` (HTTP `X-Request-ID`), `n8n_execution_id`, `n8n_item_index`, `rpc_id`, `tool`, `execution_id` and `run_id`. Invalid/oversized IDs are discarded or replaced. Trace context is reset after the entire response, including streaming/cancellation. IDs are not authorization or idempotency inputs. Search `execution_accepted` and `execution_terminal` by execution ID to join recovered/background work to the original n8n request. New structured events never include inputs, results, API keys or raw exception text.

Set a **separate random `MONITORING_TOKEN` of at least 32 characters**. Scrape the private `/health/metrics` and `/health/ready` endpoints with `Authorization: Bearer <monitoring token>`. Blank/short/mismatched tokens return 404. Do not reuse an end-user API key, publish the endpoints, or add them to the public session-auth bypass list. Readiness checks SQL, Redis and shared-router subscription state with a 3-second bound. Gateway `/health` is only a gateway liveness signal.

Metrics are process-local; scrape each one-worker replica separately and aggregate. Multiple workers behind a randomly routed metrics port cannot provide reliable per-process counters. Counters reset on restart. Labels contain only bounded route/status/outcome/error categories, never owners, execution IDs or arbitrary URLs.

| Metric                                | Meaning                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| `astron_http_requests_total`          | HTTP request counts by bounded route and status class                           |
| `astron_http_duration_seconds_*`      | HTTP duration histogram/count/sum, including streaming response lifetime        |
| `astron_mcp_calls_total`              | Successful/error control calls; acceptance is not business success              |
| `astron_executions_accepted_total`    | Newly committed execution receipts, excluding idempotent replays                |
| `astron_execution_transitions_total`  | Confirmed terminal transitions, counted after the SQL update succeeds           |
| `astron_execution_errors_total`       | Allowlisted terminal error codes                                                |
| `astron_execution_duration_seconds_*` | Actual Client run duration when both timestamps are available                   |
| `astron_client_busy_total`            | Confirmed managed `CLIENT_BUSY` receipts                                        |
| `astron_rate_limited_total`           | Requests rejected by the shared per-owner limit                                 |
| `astron_clients_online`               | Local owned connection count; during lease loss it can lag by at most one lease |
| `astron_ready`                        | SQL, Redis and router readiness, checked during private scrapes                 |

Example alert conditions (tune after measuring): readiness unavailable for 1 minute; expected clients absent for 2 minutes; HTTP 5xx above 5% for 5 minutes with at least 20 calls; confirmed execution failures/timeouts above 5% for 5 minutes; busy receipts above 10%; HTTP p95 above 5 seconds for 5 minutes. Count `UNKNOWN` separately from failure: investigate the original execution before resubmitting. Alert on certificate expiry below 14 days and storage usage above 80% using the deployment's certificate/host monitoring.

[monitoring-alerts.yml](monitoring-alerts.yml) contains the application alert rules. Load it into the existing monitoring deployment and route alerts to the operator's configured receiver; the application does not send external notifications itself. Disable the always-online Client rule where unattended connectivity is not expected.

## Limits, capacity and failure handling

`INTEGRATION_RATE_PER_MINUTE=0` keeps the limit disabled for compatibility. A positive value enables a 60-second fixed window per **authenticated owner**, shared across MCP, REST, API keys for that owner and replicas. Over-limit calls receive 429 `RATE_LIMITED` and `Retry-After`; a broker error returns 503 before dispatch. The node reports a confirmed 429 without transport fallback. Keep the proxy's unauthenticated request/body/connection limits as a separate perimeter control. Budget initialization and polling calls, not only starts.

Routing permits at most 64 outstanding RPCs and 64 inbound handlers per process, with a 4 MiB envelope limit and bounded request deadlines. WebSocket message handling also applies backpressure. Recovery scans at most 32 records/observations per pass with a rotating cursor, so unresolved old records cannot grow a single scan without bound or permanently starve newer records. Client concurrency remains one active execution per current Client contract; more n8n workers do not create more desktop capacity. Existing JSON/file limits remain unchanged.

Measure a baseline with synthetic workflows at concurrency 1, 2 and 4, bounded duration and polling. Record n8n/Node/server/Client versions, operation, calls/s, success/busy/timeout/unknown counts, p50/p95, process memory, Redis latency and connection count. Verify no additional starts after a lost reply, idempotent replay across channels, reconnect with a new connection generation, OpenAPI restart, n8n worker restart during a persisted wait, and package upgrade/restart. Stop once the agreed bounded sample is complete; do not run an unattended load generator against a desktop.

Troubleshooting order: locate n8n execution/item → find matching `mcp_call`/HTTP trace → follow AstronRPA `execution_id` → compare Client `run_id`/receipt → inspect the safe error category. For `CLIENT_OFFLINE`, inspect login/route lease; for `UNKNOWN`, query the same receipt; for 429, reduce starts/polling; for readiness 503, check SQL/Redis privately; for TLS failure, fix the trust chain or hostname. Never resolve a stuck execution by deleting receipts, changing the business key, switching MCP/REST automatically, or clearing shared Redis/database state.

The node emits `astron_transport_failure` diagnostics even if a request never reaches the server. They contain only transport, target hostname, request trace, bounded error category and valid n8n execution/item IDs. TLS, timeout, network, HTTP 401/403/429 and other HTTP failures remain distinguishable; URL paths/query strings, credentials, bodies and raw exceptions are omitted. Logs do not change dispatch uncertainty or authorize retries. Schema denials expose a bounded public-schema field, rule and expected types in `callerError.validation`; unknown dictionary keys are represented by `*`, and input/enum values are never copied into that diagnostic. n8n execution-data retention still requires the pruning controls described in the package README.
