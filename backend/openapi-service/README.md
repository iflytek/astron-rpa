# RPA OpenAPI Service - RPA Workflow Management Service

See [external integration security, key rotation and Credentials design](EXTERNAL_INTEGRATION_SECURITY.md) for the current authentication contract and migration requirements.

## 📖 Project Introduction

RPA OpenAPI Service is an RPA workflow management service built on FastAPI, providing workflow creation, execution, monitoring, and API key management functions. The service integrates WebSocket real-time communication, MCP (Model Context Protocol) support, Redis caching, request tracing and other modern technology stacks, providing complete API service capabilities for the RPA platform.

### ✨ Key Features

- 🔄 **Workflow Management** - Support for workflow creation, update, query and deletion
- ⚡ **Real-time Execution** - WebSocket-based real-time workflow execution and status monitoring
- 🔑 **API Key Management** - Complete API key generation, validation and management functionality
- 🌐 **MCP Protocol Support** - Integration with Model Context Protocol, supporting AI model interaction
- 📊 **Request Tracing** - Complete request ID generation and passing mechanism, simplifying log tracing
- 📝 **Structured Logging** - Unified log format and log file rotation management
- ♻️ **Dependency Injection** - Clear dependency injection pattern, easy to test and maintain
- 🔄 **Redis Integration** - Async Redis connection pool for caching and distributed state management
- 🧪 **Testing Framework** - Integrated pytest-asyncio for async testing
- 🐳 **Containerized Deployment** - Docker and Docker Compose configuration

## 🏗️ Project Architecture

The service adopts a clear layered architecture design, specifically designed for RPA workflow management:

### 1. API Layer (`app/routers/`)
- **Workflow Management** (`workflows.py`) - Workflow CRUD operations
- **Execution Management** (`executions.py`) - Workflow execution and status monitoring
- **API Key Management** (`api_keys.py`) - API key generation and validation
- **WebSocket Communication** (`websocket.py`) - Real-time communication and status push
- **MCP Protocol** (`streamable_mcp.py`) - Model Context Protocol support

### 2. Service Layer (`app/services/`)
- **Workflow Service** (`workflow.py`) - Workflow business logic processing
- **Execution Service** (`execution.py`) - Workflow execution logic
- **WebSocket Service** (`websocket.py`) - Real-time communication management
- **API Key Service** (`api_key.py`) - Key generation and validation logic

### 3. Data Models (`app/schemas/`)
- **Workflow Schema** (`workflow.py`) - Workflow data structure definitions
- **Execution Schema** (`execution.py`) - Execution status and result definitions
- **API Key Schema** (`api_key.py`) - Key-related data structures

### 4. Common Components
- **Dependency Injection** (`app/dependencies/`) - User authentication, service dependency management
- **Middlewares** (`app/middlewares/`) - Request tracing middleware
- **Internal Interfaces** (`app/internal/`) - Management and maintenance interfaces

### 5. Configuration and Connection Management
- **Configuration Management** (`app/config.py`) - Environment variables and configuration management
- **Redis Connection** (`app/redis.py`) - Async Redis connection pool
- **Logging Management** (`app/logger.py`) - Unified logging configuration

## 🛠 Technology Stack

| Component | Technology | Version Requirement |
|-----------|------------|-------------------|
| **Backend Framework** | FastAPI | >=0.115.12 |
| **Python** | Python | >=3.11 |
| **Database** | MySQL + SQLAlchemy | >=2.0.41 |
| **Cache** | Redis | >=6.1.0 |
| **Async Support** | asyncio + aiomysql | >=0.2.10 |
| **Config Management** | Pydantic Settings | >=2.9.1 |
| **Containerization** | Docker + Docker Compose | - |
| **Testing Framework** | pytest + pytest-asyncio | >=8.3.5 |
| **Code Quality** | Ruff | >=0.11.11 |
| **Dependency Management** | uv | - |

## 📁 Project Structure

```
rpa-openapi-service/
├── app/                          # Main application directory
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── redis.py                  # Redis connection pool management
│   ├── logger.py                 # Logging configuration
│   ├── dependencies/             # Dependency injection modules
│   │   └── __init__.py          # Common dependency injection
│   ├── schemas/                  # Pydantic data schemas
│   │   ├── workflow.py          # Workflow data structures
│   │   ├── execution.py         # Execution status and results
│   │   └── api_key.py           # API key data structures
│   ├── routers/                  # API routes
│   │   ├── workflows.py         # Workflow management routes
│   │   ├── executions.py        # Execution management routes
│   │   ├── api_keys.py          # API key management routes
│   │   ├── websocket.py         # WebSocket communication routes
│   │   └── streamable_mcp.py    # MCP protocol support
│   ├── services/                 # Business logic services
│   │   ├── workflow.py          # Workflow service
│   │   ├── execution.py         # Execution service
│   │   ├── api_key.py           # API key service
│   │   └── websocket.py         # WebSocket service
│   ├── middlewares/              # Middlewares
│   │   └── tracing.py           # Request tracing middleware
│   └── internal/                 # Internal management interfaces
│       └── admin.py             # Admin interface
├── tests/                        # Test code
│   ├── conftest.py              # Test configuration
│   ├── test_main.py             # Main application tests
│   └── routers/                 # Route tests
├── logs/                         # Log directory
├── Dockerfile                    # Docker image build
├── pyproject.toml                # Project dependency configuration
├── uv.lock                       # uv dependency lock file
└── README.md                     # Project documentation
```

## 🚀 Core Functions

### 1. Workflow Management (`/workflows`)
- **Create/Update Workflow** (`/workflows/upsert`) - Support for workflow creation and update
- **Query Workflow** (`/workflows/{project_id}`) - Query workflow details by project ID
- **Workflow List** (`/workflows`) - Paginated workflow list query
- **Delete Workflow** (`/workflows/{project_id}`) - Delete specified workflow

### 2. Workflow Execution (`/executions`)
- **Create Execution** (`/executions`) - Create workflow execution task
- **Query Execution Status** (`/executions/{execution_id}`) - Get execution status and results
- **Execution List** (`/executions`) - Paginated execution record query
- **Cancel Execution** (`/executions/{execution_id}/cancel`) - Cancel running workflow

### 3. API Key Management (`/api-keys`)
- **Generate Key** (`/api-keys`) - Create new API key
- **Key List** (`/api-keys`) - Query user's API key list
- **Delete Key** (`/api-keys/{key_id}`) - Delete specified API key

### 4. WebSocket Real-time Communication (`/ws`)
- **Real-time Status Push** - Real-time updates of workflow execution status
- **Execution Log Stream** - Real-time push of log information during execution
- **Connection Management** - Support for multi-client connections and message broadcasting

### 5. MCP Protocol Support (`/mcp`)
- **Model Context Protocol** - Support for AI model interaction with workflows
- **Streaming HTTP Processing** - Support for streaming data transmission and processing
- **API Key Authentication** - Supports Bearer and `X-API-Key` request headers

#### MCP Authentication

Bearer authentication is recommended for production:

```http
Authorization: Bearer <API_KEY>
```

The dedicated header is also supported:

```http
X-API-Key: <API_KEY>
```

URL query credentials (`?key=`) are rejected by default so credentials do not enter browser history or proxy logs.
Set `MCP_ALLOW_QUERY_API_KEY=true` only while migrating legacy clients. A request must use exactly one credential
source. Missing, malformed, invalid, or revoked credentials return HTTP 401.

#### Stable workflow control tools

External integrations can use `https://<rpa-host>/api/rpa-openapi/mcp/` for asynchronous execution.
These tools share the REST execution core and do not depend on workflow names, n8n, or a deployment address.

| Tool | Input | Output |
| --- | --- | --- |
| `astron_integration_get` | None | Integration contract, supported operations and Client readiness; does not start work |
| `astron_workflow_list` | Optional `offset`, `limit` (1–100) | Authorized workflows, admission summaries and `nextOffset` |
| `astron_workflow_get` | `projectId` | Published version, `inputSchema`, declaration profile and actual Client cancellation capability |
| `astron_workflow_execute` | `projectId`, optional `params`, `version`, `idempotencyKey`, `executionTimeout`, `profileRevision` | Immediate execution snapshot including `executionId` |
| `astron_execution_get` | `executionId` | Execution state, result, or a safe error summary |
| `astron_execution_cancel` | `executionId` | Cancellation intent or an already confirmed terminal state |

Project IDs are strings. Starts require the authenticated user's current external-access release.
Omitting `version` selects that release. Queries recheck execution ownership, current workflow ownership and external
access. Ordinary republication preserves management of accepted executions; disabling external access, deleting
the workflow or revoking the API key denies access.

**REST compatibility change:** `GET /executions/{execution_id}` now retains access to an accepted execution
after ordinary workflow republication, returning that execution's original version. Previously, the
current-publication version check could reject this query. `GET /executions/get` likewise includes eligible
executions from earlier published versions. Execution ownership, current workflow ownership,
external access and API-key authorization are still checked; a new start still requires the current release.

Control tool names are reserved; colliding dynamic workflows remain callable by project ID. Other dynamic tools retain
their synchronous behavior.

The stable entry point accepts published JSON strings, finite numbers, booleans, arrays, objects, enums,
dates, timezone-qualified date-times and declared secret fields. Unknown fields, file/runtime objects and
unsupported parameter metadata are rejected. Approved file workflows carry opaque IDs as strings and use separate binary routes. Tools advertise input and output JSON Schemas.
Successful calls provide both `structuredContent` and equivalent JSON text. Tool errors use `isError=true` with
`error.code/message`, without echoing arguments or internal exceptions.

Managed snapshots include Client/run identity, UTC accepted/started/finished times, cancellation intent and
`resultVisibility`, which identifies results suppressed for secret inputs.
States are `accepted`, `running`, `succeeded`, `failed`, `cancelled`, `timeout`, or `unknown`.
Cancellation and execution timeout require actual stop confirmation; observation loss remains nonterminal `unknown`.
Legacy Clients/records retain their capability limitations and cannot confirm a managed cancellation.

With an upgraded Client, a stable `idempotencyKey` and identical request return the original execution ID
across retries and restarts. Calls without that key must not automatically retry a start. Never recover an
uncertain MCP start by issuing a new REST start. Poll the original ID; caller wait expiry does not stop it.
See [execution management](EXECUTION_MANAGEMENT.md) for the single-worker deployment requirement,
durable reconciliation, supported protocols, input retention, migration and rollback limits.

#### Integration admission

The [AstronRPA community node](../../integrations/n8n/n8n-nodes-astron-rpa/README.md) uses these MCP tools.
Set `INTEGRATION_POLICY_FILE` on OpenAPI to an administrator-owned JSON policy file. Its models are defined in
[`app/services/integration_policy.py`](app/services/integration_policy.py). The empty policy is:

```json
{ "schemaVersion": 1, "enforcedUsers": [], "declarations": [] }
```

An empty policy admits no workflow through the community node. Add the intended user to `enforcedUsers`
and a reviewed declaration for each approved project/version. Declarations bind the owner, project, version
and input-schema digest. They describe capabilities, an optional capability class, file inputs/outputs,
GUI/human requirements, environment, side effects, risk, execution type, exclusive-terminal requirements
and an optional output schema. The `json-data` class requires both `capabilityClass: "json-data"` and
`capabilities: ["json-data"]`; it rejects file transfer and GUI requirements and exposes bounded JSON
limits in the workflow profile.

Browser and service read classes additionally require `componentOperations`,
`allowedTransports`, no declared business side effects, and a private `readOnlyReview`:

```json
{
  "version": 1,
  "boundedResources": true,
  "readOnlyConnections": true,
  "operationInputs": {
    "Network.http_request": { "request_type": "get", "file_path": "", "save_type": "no" }
  }
}
```

The administrator must check the published workflow's actual operations and fixed arguments.
Use an array of argument objects when the same operation occurs several times; operations
without guarded switches still require `{}` entries. A direct input binding such as
`{"parameter":"method"}` requires a schema enum containing only permitted values and is
checked again at execution. SQL must be fixed, reviewed read SQL using read-only database
credentials; dynamic SQL is not admitted. This is a trusted release review, not a sandbox
or a general SQL firewall. Connection handles, element objects and iterators stay inside
the workflow; public results must satisfy the frozen JSON schema and limits.

HTTP is limited to GET/HEAD without upload or save; mail disables attachment saving and
mark-as-read; browser extraction is single-page without file/data-table export.
Each `BrowserSoftware.get_current_obj` call must explicitly pass `activate_window=False`,
with `"BrowserSoftware.get_current_obj": {"activate_window": false}` in
`readOnlyReview.operationInputs`. Omitted or enabled switches are rejected because the
component defaults to activating and maximizing the browser window. When changing workflow
arguments, republish the workflow and review that version before updating its declaration;
editing the policy alone does not change the workflow's behavior.

The public profile exposes `readContractVersion: 1`, not private SQL or review arguments. Review changes
invalidate the profile revision. MCP remains primary. An explicitly admitted REST execution
uses `?contract=1` for submission/query and `POST /executions/{id}/cancel`; these return the
same authorized snapshot as MCP. Deploy the matching gateway Lua policy for these routes.

Unknown values remain distinct from false. The supported declaration scope is `controlled-validation`;
file declarations require the independent `office-file` contract below. The data contract limits encoded JSON to 1 MiB, nesting
depth to 12, object properties to 200, array items to 1,000 and each string to 100,000 characters.

Within the enrolled user scope, fixed MCP, dynamic MCP and REST starts share admission checks; unknown,
incomplete, stale or denied declarations are rejected. Users outside this scope retain their existing entry
points but have no community-node admission. A malformed configured file rejects new starts instead of
silently disabling policy enforcement.

Each OpenAPI process caches the last successfully parsed policy by resolved path and file metadata,
including nanosecond mtime, size and file identity. Unchanged files are not reread or reparsed for every
workflow in a list. Metadata is checked on each access; file changes or atomic replacement invalidate the
cache. Publish updates by atomically replacing the file. Missing, unreadable, malformed or concurrently
changed files fail closed with `INTEGRATION_POLICY_UNAVAILABLE`, without reusing an earlier valid policy.

The public revision is a digest of the complete declaration. Changing any declaration content changes that
revision even when its human label is unchanged. `profileRevision` binds a prepared request to it.
Same-key recovery returns an authorized existing receipt without requiring a new declaration for that execution.

#### Office and file workflows

Binary storage is opt-in. Set `INTEGRATION_FILE_ROOT` to an absolute private, persistent directory available
inside OpenAPI, and `INTEGRATION_FILE_TRANSFER_URL` to its public HTTPS base ending in `/files/transfer`,
for example `https://rpa.example/api/rpa-openapi/files/transfer`. Mount that directory into the container;
keep its SQLite manifest and blobs together and outside static/public serving paths. Leaving either
setting blank prevents file admission. Deploy the matching gateway Lua policy, allow request bodies of
at least 10 MiB at the proxy, and keep TLS verification enabled. Use the existing single-worker deployment;
this local store is not distributed object storage.

Declare `capabilityClass: "office-file"`, `capabilities: ["office-file"]`, the actual component operations,
allowed execution transports, no human interaction, low/medium risk and `exclusiveTerminal: true`.
Set GUI requirements for Excel, Word and browser operations. Input/output file flags must match the contract:

```json
{
  "fileContract": {
    "version": 1,
    "limits": { "maxFileBytes": 10485760, "maxFiles": 8, "retentionSeconds": 86400 },
    "inputs": { "source": [".txt"] },
    "outputs": { "target": "result.txt" }
  },
  "fileReview": {
    "version": 1,
    "workspaceOnly": true,
    "macrosDisabled": true,
    "externalServicesReviewed": true,
    "boundedResources": true,
    "resourcesReleased": true,
    "operations": ["File.file_read", "File.file_write"]
  }
}
```

The private review's operation list must exactly match `componentOperations`. Review the published code:
all paths must derive from the supplied workspace, output files must match their declared names, Office
macros and global close/kill operations must be disabled, resource use bounded, and connections/documents
released on every exit. Declare `workspace-files` for output writes and `external-file-transfer` for external
file exchange. Approve external destinations and credentials explicitly. These checks admit trusted releases;
they do not sandbox arbitrary Python or prevent a malicious approved workflow from accessing the client.
The public profile exposes `fileContract`, but excludes the private review. The operation inventory in
`app/schemas/office_file.py` is an admission boundary, not proof every operation has been individually tested.

File parameter names must be ASCII identifiers with string schemas. Inputs contain opaque UUID handles;
outputs contain `output:<parameterName>`. The service freezes bindings, integrity metadata and output names
at acceptance. The upgraded client receives execution-bound, expiring read/write grants, prepares private
paths, uploads outputs before reporting success and removes its workspace after confirmed termination.
The execution deadline must be 1–3,600 seconds. Secret-input file workflows are rejected. The JSON result is
`{"data": <workflow result>, "files": {<output parameter>: <metadata>}}`; any `outputSchema` applies to this
whole object, and the existing JSON limits also apply before persistence.
Exact file-parameter path echoes from the executor are omitted from `data`; other workspace path
disclosures are rejected. Use the file metadata in `files` to retrieve binary outputs.

External binary routes use the same owner API-key authentication as workflow control:

| Route | Purpose |
| --- | --- |
| `POST /files` | Reserve using `fileName` and an owner-scoped `uploadKey` |
| `PUT /files/{id}/content` | Upload immutable bytes; identical retries are accepted |
| `GET /files/{id}` | Read file metadata |
| `GET /files/{id}/content` | Download authorized bytes |
| `DELETE /files/{id}` | Delete an owned file with no active grant |

Client-only `GET/PUT /files/transfer/{id}` uses a separate execution-bound bearer grant and requires an active
execution. Tokens are hashed in the manifest and are not returned in profiles/results. Output downloads and
reuse as inputs recheck successful parent execution and current workflow authorization. Files expire after
24 hours; active grants may pin them through the execution/recovery window. Cleanup runs every five minutes.
The store enforces 10 MiB per file, eight file bindings per execution, 64 records and 100 MiB allocated per
owner; pending uploads reserve 10 MiB. Grant revocation releases unused output reservations. Server paths,
client paths and caller-supplied URLs are never file identifiers.

#### Desktop and UI workflows

Use `capabilityClass: "desktop-ui"`, `capabilities: ["desktop-ui"]`, `requiresGui: true`, `exclusiveTerminal: true`, a low/medium risk declaration and `sideEffects` containing `desktop-interaction`. `componentOperations` must match the deterministic allowlist in `app/schemas/desktop_ui.py`. The client must advertise `desktopProtocolVersion: 1`; execution requires a deadline of 1–3,600 seconds. MCP and explicitly admitted REST share the same authorization, frozen contract, receipt and cancellation path.

Add these fields to the existing version-bound declaration (replace the example program and window with reviewed deployment values):

```json
{
  "desktopContract": {
    "version": 1,
    "resolution": {"width": 1920, "height": 1080},
    "programs": ["business-app"],
    "humanMode": "none"
  },
  "desktopReview": {
    "version": 1,
    "operations": ["Window.exist"],
    "programs": {"business-app": "C:/Apps/Business/app.exe"},
    "targets": ["Reviewed business window"],
    "boundedResources": true,
    "noHighRiskActions": true,
    "inputBindingsReviewed": true,
    "resourcesReleased": true
  }
}
```

`desktopReview` is private and contributes to the declaration revision. Its operations must exactly match `componentOperations`; paths must be absolute local `.exe` paths. Program identifiers are public, paths and target titles are not. These paths check installation only; they do not execute programs. Review every program argument, dynamic input, element locator, clipboard mode, browser/file switch and cleanup action against the actual published code. This does not sandbox Python or guarantee isolation from user input.

Dialog operations require `requiresHuman: true` and `humanMode: "attended"`. Managed runs use process-owned native forms (Tcl/Tk is required in the client Python runtime); ordinary designer runs retain their existing form host. The execution deadline and precise cancellation also bound native dialogs. File actions or mixed Office workflows additionally require a valid `fileContract` and `fileReview`, retaining file authorization, workspace boundaries and secret-input restrictions. No file permission is implied by desktop admission. Model-driven CUA, CAPTCHA automation, commands/scripts and destructive system control remain closed.

The client checks session availability, lock state, primary-screen resolution and installed programs before launching, then checks session/resolution and unexpected owned popups every 500 ms. Reserve the interactive terminal; periodic checks cannot prevent all GUI races. A detected environment loss requests precise cancellation and becomes a safe desktop error only after the process stops. Unconfirmed stops remain unknown. Reconnection/restart observes the original execution and never replays desktop side effects. The exclusive slot remains occupied during active execution, recovery and resource cleanup; there is no task queue.

#### AI, dynamic code and high-risk workflows

Use `capabilityClass: "ai-dynamic-risk"`, `capabilities: ["ai-dynamic-risk"]`, an explicit `outputSchema`, `exclusiveTerminal: true`, `requiresHuman: false` and `risk: "medium"` or `"high"`. Human approval is supplied by an administrator before the request, not by a caller-controlled confirmation flag or a desktop dialog. The client must advertise `riskProtocolVersion: 1`. The public contract is:

```json
{"riskContract":{"version":1,"approvalMode":"admin-exact-request","automaticExecution":false}}
```

The same declaration needs a private `riskReview`:

```json
{
  "version": 1,
  "trustedRelease": true,
  "sensitiveDataReviewed": true,
  "destinationsReviewed": true,
  "resourcesReleased": true,
  "maxOperations": 20,
  "operations": {
    "ChatAI.single_turn_chat": {"risk":"medium","argumentHashes":[]}
  },
  "codeHashes": [],
  "approvals": [{
    "id":"request-approval-id",
    "approvedBy":"administrator-id",
    "paramsHash":"<SHA-256 of bound input JSON>",
    "keyHash":"<SHA-256 of JSON-encoded business key>",
    "executionTimeout":60,
    "issuedAt":1792627200,
    "expiresAt":1792630800
  }]
}
```

Replace placeholders and timestamps before enabling admission. `operations` must exactly match `componentOperations`; `maxOperations` is 1–10,000. Approval validity is at most 24 hours and the execution timeout is 1–3,600 seconds. Approval entries are unique by ID and business-key hash. The declaration binds the owner, project, release, input schema and revision; every private review change also changes the revision. Hash JSON with the service's `execution_management.digest` (sorted keys, compact separators, ASCII escaping, finite values), after input defaults are bound. The key is hashed as a JSON string, not as unquoted text.

Only the non-agent inference operations listed in `INFERENCE_OPERATIONS` may have empty `argumentHashes`. All other calls require one or more exact argument digests, including helper operations in a mixed workflow. Compute those with the client's `actionlib.managed_risk.argument_digest` against the actual function signature: defaults and enums are normalized, local handles are represented by type, and managed workspace paths use `$workspace/`. Model-selected write arguments must match these reviewed hashes. Never approve a hash without reviewing the corresponding arguments and destination.

`Smart.run_code`, `Script.*` and `BrowserScript.js_run` additionally require SHA-256 `codeHashes` of the published source bytes (browser script content uses UTF-8). Review imports, package dependencies, subprocess behavior and irreversible effects as part of the trusted release. Runtime checks verify atomic calls and directly invoked code; they are not a Python sandbox or an OS access-control mechanism. Operations requiring an autonomous computer-use host, CAPTCHA handling, desktop unlock or designer-dependent multi-turn/knowledge chat are deliberately denied in `app/schemas/ai_dynamic_risk.py`.

File and GUI combinations need the same bounded file bindings/private file review and desktop environment/private desktop review used elsewhere. No category inheritance grants those permissions. File workflows with secret inputs remain unsupported. The `desktopReview.noHighRiskActions` assertion applies to the `desktop-ui` category; risk-category actions require their own exact request and argument approval instead. Set `sideEffects` to the applicable values: `external-service`, `external-write`, `dynamic-code`, `desktop-interaction`, `workspace-files`, `external-file-transfer`.

MCP and explicitly admitted REST enforce the same approval before dispatch. Legacy dynamic tool discovery omits these workflows; fixed tools still require approval. Repeating an already accepted request with its original key and revision returns its receipt even after approval expiry/removal, without another dispatch. Changed inputs, release or timeout require a new approval/key. Successful results are checked against the frozen schema and JSON limits before persistence.

For workflows accepting secret inputs, the public result is suppressed to `null`; declare a nullable output schema (for example, `{"type": ["object", "null"], "additionalProperties": true}`). An object-only schema rejects that suppressed result. This does not enable secret-input file workflows.

The existing `Execution.data_contract` stores the frozen approval and risk rules. The client's execution receipt directory also stores a private `.risk.json` contract and `.risk.audit.jsonl` events containing operation IDs, argument/code hashes and acceptance/denial. Keep these with execution audit records; do not publish private policy or audit files. Prompts, credentials and code bodies are omitted from these audit events, and managed risk diagnostic reports suppress business values. n8n execution records still follow the host's retention settings; configure execution-data pruning separately.

## 🚀 Quick Start

### Environment Requirements

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (optional)

### 1. Install Dependencies

```bash
# Install using pip
pip install -e .

# Or use uv (recommended)
uv sync
```

> It is recommended to use [uv](https://github.com/astral-sh/uv) for dependency management. The `uv.lock` file has locked dependency versions to ensure environment consistency.

### 2. Configure Environment Variables

There are three configuration files, sorted by priority from low to high: `.env.default` < `.env` < `.env.local`, where `.env.local` is only used for local debugging and should never be used in production.

Create `.env` file and configure necessary environment variables:

```bash
# Database configuration
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/rpa_openapi

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Application name
APP_NAME="RPA OpenAPI Service"

# Enable temporarily only while migrating legacy MCP clients
MCP_ALLOW_QUERY_API_KEY=false
```

### 3. Start Service

```bash
# Use uvicorn directly (development environment)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8020

# Or use uv
uv run python run.py dev
```

### 4. Verify Service

Visit [http://localhost:8020/docs](http://localhost:8020/docs) to view API documentation.

## 📚 API Documentation

FastAPI automatically generates interactive documentation for your API:

- **Swagger UI**: `/docs` - Suitable for development and debugging
- **ReDoc**: `/redoc` - More suitable for reading and sharing

## 🧪 Development Guide

### Running Tests

```bash
# Start test database
docker-compose -f docker-compose.test.yaml up -d

# Run all tests
pytest

# Run specific test file
pytest tests/routers/test_workflows.py

# Run tests with coverage
pytest --cov=app
```

### Code Quality Check

```bash
# Format code
ruff format

# Check code quality
ruff check

# Fix auto-fixable issues
ruff check --fix
```

### View Logs

```bash
# Real-time view of application logs
tail -f logs/app.log
```

### Configuration Adjustment

The service uses layered configuration files that can be created and modified as needed:

1. `.env.default` - Default configuration, committed to version control
2. `.env` - Environment-specific configuration, customized according to deployment environment
3. `.env.local` - Local development configuration, not committed to version control

Configuration loading order: `.env.default` < `.env` < `.env.local`

## 📝 Logging

### Log Configuration

- **Log Level**: Configured via `LOG_LEVEL` environment variable (default: INFO)
- **Log Directory**: Configured via `LOG_DIR` environment variable
- **Log Format**: Contains timestamp, module name, request ID, log level and message content

### Request Tracing

Each request is assigned a unique Request ID for easy troubleshooting:

```
2025-06-06 10:30:15 - app.main - [abc-123-def] - INFO - Root endpoint accessed!
```

Request ID automatically:
1. Saved in context variables for easy access throughout request lifecycle
2. Added to response header `X-Request-ID`
3. Injected into each log record

## ❓ FAQ

### Q: How to modify default port number?

A: You can specify through environment variables or directly in startup command:

```bash
# Specify in command
uvicorn app.main:app --host 0.0.0.0 --port 8020

# Or modify mapping in docker-compose.yml
ports:
  - "8020:8020"
```

### Q: How to handle large concurrent requests?

A: Consider the following solutions:
1. Increase uvicorn workers: `--workers 4`
2. Use Gunicorn as process manager
3. Use async processing for time-consuming operations
4. Add appropriate caching mechanisms

### Q: How to monitor service health?

A: You can monitor through:
1. Implement health check endpoint `/health`
2. View log files to understand detailed running status
3. Monitor Redis and MySQL connection status
4. Add Prometheus and Grafana monitoring (advanced)

### Q: How to deploy to production?

A: Recommended production deployment solutions:
1. Use Docker Compose or Kubernetes to manage containers
2. Configure reverse proxy (like Nginx) to handle SSL and request distribution
3. Use environment variables to inject sensitive configurations
4. Set appropriate log levels and monitoring

## 🔄 Contributions

If you have any improvement suggestions or questions, welcome to contribute through:

1. Submit Issues to report problems or suggest new features
2. Submit Pull Requests to contribute code improvements

## 📜 License

This project is licensed under the MIT License. You are free to use, modify and distribute this code for both personal and commercial projects.
