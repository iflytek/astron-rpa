# Workflow examples

Import these JSON files into a self-hosted n8n instance with `@iflytekopensource/n8n-nodes-astron-rpa` installed. Select your credentials on every Astron-RPA node, replace project/version placeholders, and use a published workflow approved by the server administrator. The examples configure n8n; they do not create or approve RPA workflows and contain no deployment endpoints or credentials. See the [user guide](../README.md) for setup and limits.

## Execute and query

[execute-and-query.json](execute-and-query.json) submits asynchronously and queries the returned execution ID once. Replace its business key with one appropriate to your request. Query returns the current state and does not imply completion. To wait durably for completion, set Execute to **Wait**; no external Wait loop is required. Use **Cancel Execution** with the exact ID when cancellation is intended.

## Office and files

[office-file.json](office-file.json) demonstrates Binary Data → Upload File → MCP Execute/Wait → Download File. It expects a `.txt` input binding named `source` and output binding named `target`. The preparation nodes create a small synthetic text file; replace them with your own binary source. Select credentials on all three Astron-RPA nodes.

Default error handling stops before download if execution fails. Delete input/output handles when no longer needed or let them expire. Neither handle is a client path. This text-file example does not require Office; workflows that manipulate Office documents also need a compatible COM provider and the reviewed file contract.

## Desktop and attended workflows

[desktop-ui.json](desktop-ui.json) uses MCP, Wait mode and a 60-second RPA deadline. Reserve an unlocked Windows session, match the declared primary-screen physical resolution and install the reviewed software. Administrators bind targets and program paths to the published workflow; this example supplies neither. For attended workflows, remain available to answer native forms. Cancel by the returned execution ID if intervention is needed.

## Handling errors and reruns

On native error output, `$json.error` contains a safe JSON envelope. `JSON.parse($json.error).executionId` returns an ID only when one is available; admission errors may occur before acceptance. Query uncertain executions using their original identity. Reusing a business key with changed inputs causes a conflict; creating a new key may start another RPA run.
