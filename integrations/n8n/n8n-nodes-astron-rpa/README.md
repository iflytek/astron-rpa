# Astron-RPA for n8n

Run published Astron-RPA workflows from n8n to process data, read browser and service information, work with Office documents and files, automate Windows desktop tasks, and call approved AI/code workflows.

The node submits work to your Astron-RPA server, the connected Windows client executes it, and n8n receives the execution status and result. MCP is the primary channel; workflows can also allow explicit REST execution, and files transfer over HTTPS.

**Package:** `@iflytekopensource/n8n-nodes-astron-rpa` · **Version:** `0.1.0` · **Node name:** `Astron-RPA`

[Features](#features) · [Installation](#installation) · [Configuration](#configuration) · [Quick start](#quick-start) · [Operations](#operations) · [Examples](#examples) · [Workflow requirements](#workflow-requirements) · [Troubleshooting](#troubleshooting) · [Updating or uninstalling](#updating-or-uninstalling)

## Features

| Workflow category                | What you can do                                                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| JSON and data                    | Transform strings, numbers, lists, dictionaries and other JSON values                                                          |
| Browser and service reads        | Read browser pages, make HTTP GET/HEAD requests, inspect FTP metadata, query databases, receive mail and read shared variables |
| Office and files                 | Upload input files, process documents or tabular data, and download workflow outputs                                           |
| Desktop and UI                   | Run reviewed window, element, keyboard/mouse, image and attended form actions                                                  |
| AI, code and high-risk workflows | Call configured models/Agents, run reviewed published code and perform explicitly approved side effects                        |

Across these categories, the node provides workflow discovery, asynchronous execution, durable waiting, status queries, cancellation and business-key deduplication. The server administrator approves the operations and inputs of each published workflow version.

## Installation

### Requirements

| Component         | Requirement                                                                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| n8n               | Self-hosted n8n with Node.js **24 or newer** on each executing host/container. Tested with n8n `2.40.7` / Node `24.18.0`; package peer dependency is `n8n-workflow >=2.36.4 <3` |
| Astron-RPA server | Trusted HTTPS MCP endpoint, integration contract `1`, profile schema `1` and MCP protocol `2025-11-25`                                                                          |
| Astron-RPA client | Compatible Windows client, started through the desktop application, logged in and connected to the server                                                                       |
| Workflow          | Published version with external calls enabled and an administrator-approved integration policy                                                                                  |

Install the software used by your RPA workflow on the client machine, such as a browser with the Astron-RPA extension, an Office COM provider or database drivers. See [workflow requirements](#workflow-requirements) and the [compatibility guide](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/COMPATIBILITY.md).

### Install through n8n

1. Sign in to n8n as an owner/admin and open **Settings → Community Nodes → Install**.
2. Enter `@iflytekopensource/n8n-nodes-astron-rpa@0.1.0` and complete the installation dialog.
3. Open a workflow, add a node and search for **Astron-RPA**.

Community package installation must be enabled in your n8n deployment. For queue mode, install the same package version on main and every worker, then restart those processes.

### Install from the command line

Run the commands as the account that runs n8n. The following examples use the default community package directory; use your deployment's directory if you changed the n8n user folder.

**Linux/macOS or a container shell:**

```sh
mkdir -p ~/.n8n/nodes
cd ~/.n8n/nodes
[ -f package.json ] || npm init -y
npm install @iflytekopensource/n8n-nodes-astron-rpa@0.1.0
```

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE/.n8n/nodes" | Out-Null
Set-Location "$env:USERPROFILE/.n8n/nodes"
if (!(Test-Path -LiteralPath package.json)) { npm init -y }
npm install @iflytekopensource/n8n-nodes-astron-rpa@0.1.0
```

Restart n8n after installation. In Docker, run the installation inside the n8n container as its runtime user and keep the community package directory on persistent storage. This installs the n8n node; the RPA workflow runs on the connected Windows client.

To install a package archive, run this in the same community package directory, replacing the path with your `.tgz`:

```sh
npm install /absolute/path/iflytekopensource-n8n-nodes-astron-rpa-0.1.0.tgz
```

Keep that archive at a durable path while `package.json` references it through `file:`. For building a package from source, see the [build instructions](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/OPERATIONS.md#build-and-release).

## Configuration

Configure the node connection in n8n Credentials, and configure the server and client in their own deployment. For an existing Astron-RPA installation, ask its administrator to confirm the server settings below before the first execution.

| Where                                  | Required configuration                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| n8n Credentials                        | Set **MCP Endpoint**, **API Key** and **MCP Protocol** as shown in [Quick start](#2-connect-n8n-to-astron-rpa). The node derives its REST and file API routes from this endpoint and uses the same credential; there is no separate REST credential to configure.                                                                                                                                                                                                                 |
| Astron-RPA gateway                     | Provide a trusted HTTPS address reachable from n8n and the client, with the matching MCP, execution and file routes. Use the deployment's real hostname and port. See [HTTPS setup](https://github.com/iflytek/astron-rpa/blob/main/docker/HTTPS_DEPLOYMENT.md).                                                                                                                                                                                                                  |
| OpenAPI workflow admission             | Set `INTEGRATION_POLICY_FILE` to a private administrator-owned JSON file readable by the OpenAPI process. Add the workflow owner to `enforcedUsers` and a reviewed declaration to `declarations`, binding the project, published version and input schema. An empty policy admits no workflow through this node. See the [policy format and capability-specific fields](https://github.com/iflytek/astron-rpa/blob/main/backend/openapi-service/README.md#integration-admission). |
| Astron-RPA client                      | Point the client's server configuration to the same deployment, launch the desktop application, and log in as the workflow owner. Install the software and drivers needed by the workflow; keep the required browser page or Windows session ready. See [workflow requirements](#workflow-requirements).                                                                                                                                                                          |
| OpenAPI file storage, when using files | Set `INTEGRATION_FILE_ROOT` to an absolute private persistent directory and `INTEGRATION_FILE_TRANSFER_URL` to the client-reachable HTTPS transfer address ending in `/files/transfer`, for example `https://rpa.example.com/api/rpa-openapi/files/transfer`. Both settings are required for file admission. See [Office and files](#office-and-files).                                                                                                                           |
| n8n queue mode, when used              | Install the same node package on main and every worker. Share the n8n database and encryption key, and configure PostgreSQL, Redis, the public resume-webhook address and supported Binary Data storage. Follow the [queue configuration](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/OPERATIONS.md#queue-mode).                                                                                                                                             |

For container deployments, pass the OpenAPI settings into the service and mount its policy file and persistent file directory at the configured container paths. Apply environment changes by restarting or recreating the affected service. Policy-content changes are detected automatically; publish reviewed changes by atomically replacing the policy file. Keep API keys in n8n Credentials and private policies on the server. Configure n8n [execution-data retention](#sensitive-inputs-and-retention) for your deployment.

## Quick start

### 1. Prepare an RPA workflow and API key

In Astron-RPA, publish the workflow and enable external calls for it. Ask the server administrator to approve that published version, its input/output schema and its operations in the [integration policy](https://github.com/iflytek/astron-rpa/blob/main/backend/openapi-service/README.md#integration-admission). Keep the client logged in under the workflow owner's account.

Under that account, open the client's settings, select **API keys → Astron RPA Authorization**, and create an API key. Obtain the deployment's full HTTPS MCP address from the administrator, for example:

```text
https://rpa.example.com/api/rpa-openapi/mcp/
```

Use the hostname, port and path configured for your deployment. If the server currently exposes only HTTP, configure [TLS termination](https://github.com/iflytek/astron-rpa/blob/main/docker/HTTPS_DEPLOYMENT.md) first.

### 2. Connect n8n to Astron-RPA

Create and save an n8n workflow with **Manual Trigger → Astron-RPA**. On the Astron-RPA node, create **Astron-RPA MCP API** credentials:

| Field        | Value                                                                        |
| ------------ | ---------------------------------------------------------------------------- |
| MCP Endpoint | Full HTTPS address ending in `/mcp/`, including any configured port and path |
| API Key      | The workflow owner's API key                                                 |
| MCP Protocol | `2025-11-25`                                                                 |

Save the credentials and run the connection test. A successful test reports `MCP connection valid` and the client's state. It checks connectivity and protocol without starting a workflow. A client reported as offline needs to be connected before execution.

TLS certificate and hostname checks stay enabled. HTTP endpoints, URL credentials, query strings and redirects are rejected. Keep the API key in the credential field.

### 3. Select and execute a workflow

Set **Operation** to **List Workflows** and run the node. Select a project from `workflows`, then use **Get Workflow** with its **Project ID** to inspect `version`, `inputSchema` and `profile.admission`. The workflow must have `profile.admission.allowed: true`.

For the first run, use a simple approved JSON workflow. The following example assumes it accepts a string input named `message` and returns that message; adapt the inputs to your workflow's schema.

| Parameter                     | Example value                        |
| ----------------------------- | ------------------------------------ |
| Operation                     | Execute                              |
| Project ID                    | The project ID returned by discovery |
| Published Version             | The version returned by Get Workflow |
| Inputs (JSON)                 | `{"message":"Hello from n8n"}`       |
| Mode                          | Wait — Durable                       |
| Transport                     | MCP (Primary)                        |
| Business Idempotency Key      | Leave empty for this first JSON run  |
| Wait Budget (Seconds)         | `300`                                |
| Poll Interval (Seconds)       | `5`                                  |
| RPA Deadline (Seconds)        | `60`                                 |
| MCP Request Timeout (Seconds) | `15`                                 |

Execute the saved n8n workflow. **Wait** pauses while the RPA task runs and returns its confirmed result. Leaving the business key empty generates a key for this n8n execution; manually running it again creates a new request. For recovery across n8n executions, use an explicit business key as described under [execution behavior](#execution-behavior-and-errors).

To take the message from a preceding n8n node, switch **Inputs (JSON)** to expression mode and use:

```text
{{ JSON.stringify({ message: $json.message }) }}
```

### 4. Use the result or query the execution

A successful response includes these fields; this is an illustrative subset for the message workflow:

```json
{
  "executionId": "00000000-0000-4000-8000-000000000001",
  "status": "succeeded",
  "terminal": true,
  "result": { "message": "Hello from n8n" }
}
```

In the next n8n node, use `{{ $json.result.message }}` for the message or `{{ $json.executionId }}` for the execution identity. Arrays remain inside `result`; they are not split into additional n8n items.

For an asynchronous run, select **Async — Return Execution ID**. Connect a second Astron-RPA node using **Get Execution**, and set **Execution ID** to `{{ $json.executionId }}`. It returns the current snapshot; check `status` and `terminal`. To stop that execution, use **Cancel Execution** with the same ID and query again to confirm the outcome.

## Operations

| Operation        | Purpose and output                                                                                                            |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| List Workflows   | One page per input item, with `workflows` and `nextOffset`. To fetch another page, use `nextOffset` as Offset; Limit is 1–100 |
| Get Workflow     | Published version, input schema, capability declaration and admission reason                                                  |
| Execute          | Submit a published workflow using one of the modes below                                                                      |
| Get Execution    | Current status, result and error information for one execution                                                                |
| Cancel Execution | Request cancellation of the exact execution ID                                                                                |
| Upload File      | Read an n8n Binary Data property and return an owned file handle                                                              |
| Download File    | Download an authorized file into an n8n Binary Data property                                                                  |
| Delete File      | Remove an owned file with no active execution grant                                                                           |

| Execute mode                | Behavior                                                      |
| --------------------------- | ------------------------------------------------------------- |
| Async — Return Execution ID | Return the accepted execution identity for later queries      |
| Wait — Durable              | Wait through persisted n8n checkpoints for the same execution |
| Sync — Short Wait           | Use the waiting path with a budget capped at 30 seconds       |

Discovery, preparation, **Get Execution** and **Cancel Execution** use MCP. The **Transport** setting on **Execute** selects the admitted execution path; REST execution also uses MCP discovery. File transfer uses separate HTTPS REST routes. An uncertain request does not trigger an automatic transport switch.

## Examples

Download an example JSON file and use **Import from File** in the n8n workflow menu. Save the workflow, select your credentials on each Astron-RPA node, and replace project/version placeholders with your approved RPA workflow.

| Example                                              | Flow                                                                   |
| ---------------------------------------------------- | ---------------------------------------------------------------------- |
| [Execute and query](examples/execute-and-query.json) | Manual Trigger → Async Execute → Get Execution                         |
| [Office and files](examples/office-file.json)        | Sample text → Binary Data → Upload File → Execute/Wait → Download File |
| [Desktop and UI](examples/desktop-ui.json)           | Manual Trigger → Execute/Wait for an approved desktop workflow         |

The file example expects a `.txt` input binding named `source` and an output binding named `target`. It supplies sample text; the published RPA workflow supplies the processing logic. The desktop example requires your reviewed program and target configuration. See the [example instructions](examples/README.md).

## Workflow requirements

Use **Get Workflow** to inspect `profile.capabilityClass`, `componentOperations`, `allowedTransports` and `admission.allowed`. Mixed workflows must meet each applicable file, desktop and risk contract. Element handles, generators and database connections stay inside the RPA workflow; the node exchanges JSON and authorized file handles. Administrator review applies to trusted published code and is not a Python, SQL or desktop sandbox.

### JSON and service reads

JSON limits are **1 MiB** of compact UTF-8 business data, depth **12**, **200** object properties, **1,000** array items and **100,000** characters per string. Values such as `0`, `false`, `null` and nested arrays/objects retain their types. Invalid or oversized values are rejected. Results must meet the output schema and limits frozen at acceptance; execution metadata is separate from the business-result byte allowance.

- **JSON/data workflows:** use low-risk operations without files, GUI, human interaction or declared side effects.
- **Browser:** keep the intended page active in the browser connected to the Astron-RPA extension. Read-only workflows set `activate_window=False` on `BrowserSoftware.get_current_obj`. Changing workflow arguments requires republication and renewed administrator review.
- **HTTP/FTP:** use reviewed GET/HEAD requests and FTP metadata operations. Uploads and file exports require their corresponding workflow contract.
- **Mail:** keep `mask_as_read_flag` and `save_attachment_flag` disabled for read-only queries. Unread messages can appear again on later runs; deduplicate them in the calling workflow.
- **Database:** use fixed, reviewed SQL and a read-only account. SQLite requires `connect_info.read_only: true`; other types may need an [optional driver](https://github.com/iflytek/astron-rpa/blob/main/FAQ.md#q-which-drivers-do-database-workflows-need) installed on the client.

### Office and files

The administrator configures `INTEGRATION_FILE_ROOT`, `INTEGRATION_FILE_TRANSFER_URL` and the workflow's file bindings as described under [Configuration](#configuration). Keep the file directory outside public/static serving paths and allow uploads of at least 10 MiB through the gateway. The client needs file transfer protocol `1`.

1. **Upload File** reads **Binary Property** (default `data`) and returns `fileId`, `fileName`, `size`, `sha256` and `expiresAt`.
2. **Execute** takes input file IDs and output placeholders. For `source` and `target` bindings, use `{"source":"<fileId>","target":"output:target"}`. Set **RPA Deadline (Seconds)** to 1–3,600.
3. Successful output has `result.data` for workflow JSON and `result.files` for file metadata. Pass `{{ $json.result.files.target.fileId }}` to **Download File → File ID** and choose the output Binary Property.
4. Use **Delete File** for handles you no longer need, or let them expire. Downloads and reuse require authorization and a successful original execution; active grants prevent deletion.

Transfers validate size and SHA-256. Limits are **10 MiB per file**, **eight input/output bindings combined**, **24-hour retention**, and **64 records / 100 MiB allocated storage per owner**. Pending uploads reserve the maximum file size. Upload retries within the same n8n execution/node/run/item require identical bytes; a new n8n execution creates a new upload.

Use the paths supplied in the workflow's private workspace. Office workflows use private Excel/Word or WPS COM instances with macros disabled. Attaching to a user's open document or globally terminating Office processes is outside this category. File workflows with secret-marked inputs are rejected because binary outputs cannot use JSON result suppression.

DataTable exports CSV, XLSX and JSON; use XLSX for workbook output. CSV formula cells contain formula expressions, not recalculated results.

### Desktop and attended workflows

Reserve an unlocked Windows session at the declared primary-screen resolution in **physical pixels**. Keep the client logged in and install the reviewed software. User input, focus changes, popups and DPI/layout changes can affect execution. Set **RPA Deadline (Seconds)** to 1–3,600.

The client checks the declared environment and requests a stop on a session, resolution or popup violation. An unconfirmed stop remains `unknown`. Attended workflows need a person to answer their native forms and Tcl/Tk in the client runtime; their deadline continues while waiting. Screenshots also require the file contract.

Model-driven computer use, CAPTCHA automation, screen unlock, process-wide termination and arbitrary local-file selection are not enabled by desktop admission.

### AI, code and high-risk workflows

Provide an explicit **Business Idempotency Key** and **RPA Deadline (Seconds)** of 1–3,600. The administrator preapproves the exact version, inputs, business key and deadline in the server policy. The client checks approved operations, argument hashes, call counts and published code hashes; generated code needs its own approval before execution.

Chat workflows using the Astron-RPA AI service need the administrator to set `AICHAT_BASE_URL` (the provider's OpenAI-compatible API base, such as `https://model.example.com/v1`) and `AICHAT_API_KEY` on that service. The provider must serve the model ID used by the published workflow. Keep the model key in the AI service's private configuration; the n8n credential uses the Astron-RPA API key. Agent integrations need their own reviewed provider settings.

File or desktop combinations also need their respective contracts. Autonomous computer use, CAPTCHA handling, desktop unlock and designer-dependent multi-turn/knowledge chat remain denied.

## Execution behavior and errors

| Setting             | Meaning                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------- |
| MCP Request Timeout | Bounds one network request; a timeout does not establish the RPA outcome                    |
| Wait Budget         | Ends node waiting while retaining a known execution ID; does not stop RPA                   |
| RPA Deadline        | Requests process stop at the execution deadline; `timeout` requires confirmed stop evidence |

Wait handles input items sequentially. An unresolved prior execution blocks later starts, including with continuation on error enabled. A confirmed failure may continue to the next item. Async submits sequentially without waiting for client availability. A busy client rejects a new start. Cancellation targets one execution and cannot undo completed business effects.

Automatic keys are isolated by n8n execution, node, run and item. **A manual rerun or a new n8n execution creates a new automatic key.** To recover across executions, preserve an explicit business key, version, inputs and deadline. A matching same-key replay returns the original execution, including its failure; changed request content produces `IDEMPOTENCY_CONFLICT`. Use a new key only for an intentionally new business operation. n8n **Retry On Fail** does not repeat a failed business operation returned by durable waiting.

For recovery after an admission change, **Frozen Declaration Revision** can carry the original `correlation.profileRevision` for an existing matching receipt. It does not authorize a new unapproved start. An accepted receipt remains queryable after ordinary republication, subject to current ownership, external-access and credential authorization.

Persisted waiting checkpoints can resume after restart, with a possible waiting-scanner delay. A crash during an active step can leave a child execution crashed and its parent waiting. Query the original RPA receipt before recovering n8n; resolve waits before upgrading the package. Keep the original ID/key after a lost response.

Execute follows n8n's stop/continue/error-output settings. Query and Cancel return snapshots as data. On native error output, `$json.error` contains a JSON envelope; `JSON.parse($json.error).executionId` reads an available ID. Preparation or admission errors may have no ID. `INVALID_ARGUMENTS` can include a public-schema field, rule and expected types in `callerError.validation`, with values omitted.

## Sensitive inputs and retention

Astron-RPA suppresses the JSON result for secret-marked inputs: `resultVisibility: suppressed-for-secret-inputs` explains a null result. **Inputs can still be saved in n8n execution storage.** Keep API keys in credentials.

Wait and Sync create child executions that save successful and failed execution data, including prepared requests and checkpoints. Disabling successful-data storage on the parent does not override the child. Async inputs follow the parent's storage settings.

Restrict access to execution records and backups. Configure pruning for your retention requirements, for example:

```env
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
EXECUTIONS_DATA_PRUNE_MAX_COUNT=10000
```

The age is in hours. Pruning applies to eligible finished executions and does not remove backup copies; preserve unresolved waiting checkpoints. File handles and n8n execution/Binary Data storage have separate retention policies. See [n8n execution-data configuration](https://docs.n8n.io/hosting/configuration/environment-variables/executions/).

## Troubleshooting

| Symptom                                                   | What to check                                                                                                                                                  |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Astron-RPA does not appear in the node panel              | Confirm installation in the executing n8n user's community directory, Node.js version, community package settings and restart status; check every queue worker |
| Credential connection fails                               | Check the complete HTTPS host/port/path, certificate chain and API key. HTTP, URL credentials, query strings and redirects are rejected                        |
| Workflow list is empty or admission is denied             | Publish the workflow, enable external calls, use its owner's API key and ask the administrator to check the approved version and policy                        |
| `CLIENT_OFFLINE` or `CLIENT_BUSY`                         | Log in/connect the client or wait for its current execution to finish; busy requests are not queued                                                            |
| `INVALID_ARGUMENTS`                                       | Compare input names and types with Get Workflow's input schema; inspect any `callerError.validation` hint                                                      |
| `TRANSPORT_NOT_ALLOWED`                                   | Use MCP or ask the administrator to review whether that workflow can explicitly allow REST                                                                     |
| `RISK_APPROVAL_REQUIRED`                                  | Check the explicit business key, deadline and administrator approval for this exact request                                                                    |
| `IDEMPOTENCY_CONFLICT`                                    | Restore the original version, inputs and options for recovery; use a new key only for a new operation                                                          |
| Wait budget expired, `unknown` or `TRANSPORT_UNCONFIRMED` | Query the existing execution ID or recover with its original request/key before considering a new start                                                        |
| File upload/download fails                                | Check the Binary Property/File ID, file contract, size/quota, expiry, permissions and original execution status                                                |

For deployment diagnostics, see the [operations guide](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/OPERATIONS.md). When reporting an issue, include package/n8n/Node/client versions, the operation, safe error code and a minimal synthetic reproduction. Remove API keys, business inputs and private files from reports.

## Updating or uninstalling

Before changing versions, pause affected triggers and resolve active/waiting executions. Back up workflows, credentials, the n8n database and encryption key together.

For a package installed through the UI, manage it under **Settings → Community Nodes**. For a command-line installation, run `npm install @iflytekopensource/n8n-nodes-astron-rpa@<version>` in the same community package directory. Use the chosen version on main and every worker, restart them, and check credentials plus a small approved workflow before restoring triggers.

To remove a command-line installation, run:

```sh
npm uninstall @iflytekopensource/n8n-nodes-astron-rpa
```

Restart the executing processes afterwards. Workflows that reference Astron-RPA nodes need those nodes removed/replaced or the package reinstalled before they can execute. Package removal does not remove RPA workflows, server/client execution receipts or n8n's stored execution data.

### Migrating from the unscoped development package

Resolve existing waits with the old package before switching. In exported workflow definitions, change only each Astron-RPA node's `type` from `n8n-nodes-astron-rpa.astronRpa` to `@iflytekopensource/n8n-nodes-astron-rpa.astronRpa`. Keep node IDs, names, parameters, connections and credential references. Internal name `astronRpa`, type version `1` and credential type `astronRpaApi` remain unchanged.

Remove the old package, install the scoped package on all processes, restart and import the migrated workflows. Loading both packages registers the same credential type and should be avoided. Check credentials, an approved execution and persisted waiting before restoring triggers. The bundled examples use the scoped type.

## Documentation and support

| Document                                                                                                                        | Contents                                                 |
| ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [Examples](examples/README.md)                                                                                                  | Importable execution, file and desktop workflows         |
| [Server configuration](https://github.com/iflytek/astron-rpa/blob/main/backend/openapi-service/README.md#integration-admission) | Workflow admission and capability contracts              |
| [Compatibility](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/COMPATIBILITY.md)                              | Host, client, software and protocol combinations         |
| [Operations](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/OPERATIONS.md)                                    | Deployment, monitoring, upgrades and package maintenance |
| [Validation](https://github.com/iflytek/astron-rpa/blob/main/integrations/n8n/VALIDATION.md)                                    | Dated test results and pending checks                    |
| [Issues](https://github.com/iflytek/astron-rpa/issues)                                                                          | Bug reports and feature requests                         |

## License

Licensed under [Apache-2.0](LICENSE).
