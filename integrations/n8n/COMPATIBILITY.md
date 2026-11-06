# Compatibility and upgrade policy

This guide defines runtime requirements, tested environments, contract compatibility and upgrade rules. Dated test results, artifact hashes and pending checks are in [VALIDATION.md](VALIDATION.md); deployment procedures are in [OPERATIONS.md](OPERATIONS.md).

## Runtime and deployment matrix

The current package is `@iflytekopensource/n8n-nodes-astron-rpa@0.1.0`. Workflows require administrator admission of a published version and use `supportScope: controlled-validation`.

| Layer            | Requirement or supported configuration                                                       | Tested configuration and limits                                                                                                                                           |
| ---------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| n8n              | Self-hosted; Node.js `>=24`; peer `n8n-workflow >=2.36.4 <3`                                 | Scoped candidate tested on n8n `2.40.7` / Node `24.18.0`; other host versions require validation                                                                          |
| Node package     | Same tarball on main and every worker; MCP JS SDK `1.32.2` with bundled runtime dependencies | Clean consumer installation and regular/isolated queue checked on 2026-10-26                                                                                              |
| Server           | Integration contract `1`, profile schema `1`; authenticated HTTPS gateway                    | Node selects MCP wire protocol `2025-11-25`; SDK version is not a wire-protocol version                                                                                   |
| Client           | Compatible Windows desktop application and Engine; managed execution protocol `1`            | Full client `1.1.8` built/installed on 2026-10-23; current Engine source checked on 10-26, without a new full EXE build                                                   |
| Queue            | PostgreSQL and private Redis; shared n8n database/key; supported Binary Data storage         | n8n `2.40.7`, PostgreSQL `17.11`, Redis `7.0.15`, inline `default` Binary Data persisted in execution data tested; filesystem and external object storage not established |
| OpenAPI replicas | Redis routing on all replicas, same database/policy and file store                           | Two replicas on one host tested on 2026-10-23; mixed local/Redis routing and separate replica file stores unsupported                                                     |
| File store       | Persistent local files and SQLite metadata with working locks                                | Same-host shared mount supported by the tested topology; multi-host network filesystems not tested                                                                        |

The tested versions describe functional compatibility, not security clearance. The separate 2026-10-27 dependency audit found unresolved development and installed-host advisories; see [current findings and release gates](VALIDATION.md#当前验收范围与待办).

The 2026-10-26 candidate tests cover representative JSON, HTTP, text-file and window-existence workflows, approved HTTP writes, lifecycle and persisted waiting recovery. The latest interactive GUI, WPS COM, remote database and full installer tests are dated 2026-10-23. A crash during an active node step can leave a child execution crashed and its parent waiting; use the [receipt-based recovery procedure](OPERATIONS.md#queue-mode).

## Capability prerequisites

Mixed workflows must satisfy each applicable contract. The catalog classifies operations, while the server policy controls admission for the published workflow version.

| Capability            | Required environment and contract                                                                                     | Test coverage and limits                                                                                                        |
| --------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| JSON/data             | Bounded JSON input/output, frozen schema, low-risk declaration                                                        | No runtime-object transfer, GUI, files or declared side effects                                                                 |
| Browser/service reads | Reviewed read contract; browser extension and intended active page when applicable; read-only database account        | 29 operations recorded on 2026-09-20; 19 rerun on 2026-10-10; subsequent runs cover representative workflows                    |
| Office/files          | File contract and client transfer protocol `1`; private workspace and compatible COM provider                         | WPS Office `12.8.2.21555` Excel/Word tested 2026-10-23; native Microsoft Office not tested                                      |
| Desktop/UI            | Desktop contract, reserved unlocked Windows session, approved software/targets and physical primary-screen resolution | Controlled window, keyboard/mouse, UIA and screenshot paths tested; not all GUI operations, screen layouts or host combinations |
| AI/code/high risk     | Exact-request administrator approval and corresponding client capabilities; provider configuration for real calls     | Synthetic HTTP/Agent tests establish the control path; no configured real model was available                                   |

SQLite was tested locally. MySQL `8.4`, PostgreSQL `14`, SQL Server `2019 Developer` and Oracle `21c XE` read-only workflows passed on 2026-10-23 with installed optional drivers; Oracle also used a native client. Access is implemented but has not been tested with an installed driver. Validate the driver/server combination used by your deployment; see [driver requirements](../../FAQ.md#q-which-drivers-do-database-workflows-need).

## Protocol and identity rules

- Package versions, MCP wire versions, integration `contractVersion`, `profileSchemaVersion`, managed client protocol and category contract versions are independent. Display `serviceVersion` is informational. Required operations and versions are checked before execution; unsupported contracts fail closed.
- The server adapter was separately probed with `2025-03-26`, `2025-06-18`, `2025-11-25` and `2026-07-28`. The modern adapter does not implement initialize, session resume or subscriptions. The node selects `2025-11-25`; the server implements the modern protocol through its separate adapter.
- MCP provides discovery/preparation and the standalone query/cancel node operations. Explicit REST selects the admitted Execute path; file transfer uses HTTPS REST. An uncertain request never authorizes automatic transport fallback.
- Published workflows use immutable `projectId`, explicit version and profile revision. Renaming does not change identity. Republishing or changing admission requires a new reviewed declaration; an accepted receipt retains its frozen contract.
- Existing execution queries can survive ordinary republication. Ownership changes, deletion, disabled external access or revoked credentials can deny access. Current approval is required for new starts. Queries return the version recorded when the execution was accepted.
- New Engine components or variable types require operation classification, admission review, bounded serialization/transfer decisions and regressions. Adding code to the catalog does not grant execution permission.

## Package migration and upgrade checks

The scoped `0.1.0` package uses saved node type `@iflytekopensource/n8n-nodes-astron-rpa.astronRpa`. The internal node name `astronRpa`, type version `1` and credential type `astronRpaApi` remain unchanged. Follow the [migration instructions](n8n-nodes-astron-rpa/README.md#migrating-from-the-unscoped-development-package), resolve old waits before changing packages and preserve workflow exports and the previous package for rollback. Do not load both packages simultaneously or assume a saved child execution can migrate across package versions.

For n8n, SDK, client or contract upgrades, run the relevant CI suites, proxy protocol tests, credentials/admission checks and actual start/query/result/error flows. Deployment upgrades and rollbacks also require identity-preserving recovery and precise cancellation checks. Preserve the database and encryption key together, execution receipts, reviewed policy and compatible client resources; never erase receipts or downgrade schema to force a retry.

Before removing or renaming a tool, requiring new inputs, or changing authentication/state semantics, document the replacement and retain the old supported contract for at least one announced migration release. Breaking changes require a new contract version and a matrix entry. A security fix may shorten the transition only with a documented maintainer decision.

The PR author/operator provides tested host versions, source/package hashes, execution identities, assertions and pending checks. Include host tests for the Windows GUI/Office, client package, database and model-provider combinations intended for release. The maintainer confirms the support scope and the disposition of outstanding checks. See [package maintenance](OPERATIONS.md#dependency-maintenance) for dependency audits.
