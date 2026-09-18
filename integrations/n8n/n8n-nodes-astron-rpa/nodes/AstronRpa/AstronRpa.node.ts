import {
  NodeOperationError,
  type ICredentialTestFunctions,
  type ICredentialsDecrypted,
  type IExecuteFunctions,
  type INodeExecutionData,
  type INodeType,
  type INodeTypeDescription,
  type IDataObject,
  type INodeProperties,
  type IWebhookFunctions,
  type IWebhookResponseData,
} from "n8n-workflow";
import {
  AstronError,
  checkIntegration,
  checkWorkflow,
  jsonObject,
  object,
  snapshot,
} from "../../mapping/contracts";
import { withMcp, safeError, type Connection } from "../../transport/mcp";
import {
  hash,
  initialState,
  stateFrom,
  step,
  type Prepared,
} from "../../execution/runner";
import { runnerWorkflow } from "../../execution/workflow";
import { scheduleWake } from "../../execution/wake";

const executeOnly = { show: { operation: ["execute"] } };
const readId = { show: { operation: ["getExecution", "cancelExecution"] } };
const executionIdPattern =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const properties: INodeProperties[] = [
  {
    displayName: "Frozen Declaration Revision",
    name: "profileRevision",
    type: "string",
    default: "",
    displayOptions: executeOnly,
    description:
      "Optional revision from a previously prepared request. Use with the same business key and original version/inputs for recovery after publication. Server authorization still applies.",
  },
  {
    displayName: "Resume State",
    name: "_resumeState",
    type: "hidden",
    default: {},
  },
  {
    displayName: "Operation",
    name: "operation",
    type: "options",
    noDataExpression: true,
    default: "listWorkflows",
    options: [
      {
        name: "List Workflows",
        value: "listWorkflows",
        action: "List workflows",
      },
      {
        name: "Get Workflow",
        value: "getWorkflow",
        action: "Get workflow declaration",
      },
      {
        name: "Execute",
        value: "execute",
        action: "Execute published workflow",
      },
      { name: "Get Execution", value: "getExecution", action: "Get execution" },
      {
        name: "Cancel Execution",
        value: "cancelExecution",
        action: "Request execution cancellation",
      },
    ],
  },
  {
    displayName: "Project ID",
    name: "projectId",
    type: "string",
    default: "",
    required: true,
    displayOptions: { show: { operation: ["getWorkflow", "execute"] } },
  },
  {
    displayName: "Published Version",
    name: "version",
    type: "number",
    typeOptions: { minValue: 1, numberPrecision: 0 },
    default: 1,
    required: true,
    displayOptions: executeOnly,
  },
  {
    displayName: "Inputs (JSON)",
    name: "params",
    type: "json",
    default: "{}",
    displayOptions: executeOnly,
  },
  {
    displayName: "Mode",
    name: "mode",
    type: "options",
    default: "async",
    displayOptions: executeOnly,
    options: [
      { name: "Async — Return Execution ID", value: "async" },
      { name: "Wait — Durable", value: "wait" },
      { name: "Sync — Short Wait", value: "sync" },
    ],
  },
  {
    displayName: "Business Idempotency Key",
    name: "idempotencyKey",
    type: "string",
    default: "",
    displayOptions: executeOnly,
    description:
      "Stable non-secret key for retries across n8n executions. Empty generates an execution/node/run/item key. Manual reruns create new intent.",
  },
  {
    displayName: "Wait Budget (Seconds)",
    name: "waitSeconds",
    type: "number",
    typeOptions: { minValue: 1, maxValue: 86400 },
    default: 300,
    displayOptions: executeOnly,
    description:
      "Caller waiting only; expiration never cancels RPA. Sync is capped at 30 seconds.",
  },
  {
    displayName: "Poll Interval (Seconds)",
    name: "pollSeconds",
    type: "number",
    typeOptions: { minValue: 1, maxValue: 60 },
    default: 5,
    displayOptions: executeOnly,
  },
  {
    displayName: "RPA Deadline (Seconds)",
    name: "executionTimeout",
    type: "number",
    typeOptions: { minValue: 0, maxValue: 86400 },
    default: 0,
    displayOptions: executeOnly,
    description:
      "0 means no process deadline; separate from the caller wait budget",
  },
  {
    displayName: "Execution ID",
    name: "executionId",
    type: "string",
    default: "",
    required: true,
    displayOptions: readId,
  },
  {
    displayName: "Offset",
    name: "offset",
    type: "number",
    typeOptions: { minValue: 0 },
    default: 0,
    displayOptions: { show: { operation: ["listWorkflows"] } },
  },
  {
    displayName: "Limit",
    name: "limit",
    type: "number",
    typeOptions: { minValue: 1, maxValue: 100 },
    default: 100,
    displayOptions: { show: { operation: ["listWorkflows"] } },
  },
  {
    displayName: "MCP Request Timeout (Seconds)",
    name: "requestTimeout",
    type: "number",
    typeOptions: { minValue: 3, maxValue: 120 },
    default: 15,
  },
  {
    displayName: "Internal Requests",
    name: "_requests",
    type: "hidden",
    default: [],
  },
  {
    displayName: "Internal Error Mode",
    name: "_continue",
    type: "hidden",
    default: false,
  },
];

function integer(
  ctx: IExecuteFunctions,
  name: string,
  index: number,
  min: number,
  max: number,
  fallback: number,
): number {
  const value = ctx.getNodeParameter(name, index, fallback);
  if (
    typeof value !== "number" ||
    !Number.isInteger(value) ||
    value < min ||
    value > max
  )
    throw new AstronError("INVALID_ARGUMENTS");
  return value;
}
function failure(
  ctx: IExecuteFunctions,
  code: string,
  value: IDataObject,
  index: number,
  keys: string[],
): INodeExecutionData {
  const details = {
    executionId: value.executionId,
    projectId: value.projectId,
    version: value.version,
    correlation: value.correlation,
  };
  const error = new NodeOperationError(
    ctx.getNode(),
    JSON.stringify({ code, ...details }),
    { itemIndex: index },
  );
  if (!ctx.continueOnFail()) throw error;
  // Native n8n error routing merges original input. Omit its values explicitly.
  return {
    json: {
      ...Object.fromEntries(keys.map((key) => [key, "[OMITTED]"])),
      ...value,
      error: { code, message: code },
    },
    error,
    pairedItem: { item: index },
  };
}

export class AstronRpa implements INodeType {
  description: INodeTypeDescription = {
    displayName: "AstronRPA",
    name: "astronRpa",
    group: ["transform"],
    version: 1,
    description: "Control published AstronRPA workflows through MCP",
    defaults: { name: "AstronRPA" },
    inputs: ["main"],
    outputs: ["main"],
    webhooks: [
      {
        name: "default",
        httpMethod: "POST",
        responseMode: "onReceived",
        path: "",
        restartWebhook: true,
      },
    ],
    credentials: [
      {
        name: "astronRpaApi",
        required: true,
        testedBy: "astronConnectionTest",
      },
    ],
    properties,
  };
  methods = {
    credentialTest: {
      async astronConnectionTest(
        this: ICredentialTestFunctions,
        credential: ICredentialsDecrypted,
      ) {
        try {
          const info = await withMcp(
            credential.data as unknown as Connection,
            15000,
            async (client) => {
              const names = await client.listTools();
              if (!names.includes("astron_integration_get"))
                throw new AstronError("CONTRACT_UNSUPPORTED");
              return checkIntegration(
                await client.call("astron_integration_get", {}),
              );
            },
          );
          return {
            status: "OK" as const,
            message: `MCP connection valid; Client ${String(object(info.client).state)}. No execution was started.`,
          };
        } catch (error) {
          return { status: "Error" as const, message: safeError(error).code };
        }
      },
    },
  };

  async webhook(this: IWebhookFunctions): Promise<IWebhookResponseData> {
    if (this.getNodeParameter("operation") !== "_pause")
      return { webhookResponse: { accepted: false } };
    const requests = this.getNodeParameter(
      "_requests",
    ) as unknown as Prepared[];
    const state = stateFrom(
      this.getNodeParameter("_resumeState"),
      requests.length,
    );
    // Ignore the callback body; only n8n's persisted execution state is trusted.
    return {
      webhookResponse: { accepted: true },
      workflowData: [[{ json: state as unknown as IDataObject }]],
    };
  }

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const operation = String(this.getNodeParameter("operation", 0));
    const inputs = this.getInputData();
    if (operation.startsWith("_")) {
      const requests = this.getNodeParameter(
        "_requests",
        0,
      ) as unknown as Prepared[];
      if (!Array.isArray(requests) || !requests.length)
        throw new AstronError("RESUME_CONTEXT_UNSUPPORTED");
      if (operation === "_state")
        return [
          [
            {
              json: initialState(
                requests,
                Date.now(),
              ) as unknown as IDataObject,
            },
          ],
        ];
      const state = stateFrom(inputs[0].json, requests.length);
      if (operation === "_pause") {
        await this.putExecutionToWait(new Date(state.nextPoll));
        scheduleWake(
          this.getWorkflowDataProxy(0).$execution.resumeUrl,
          state.nextPoll,
        );
        return [inputs];
      }
      if (operation === "_step") {
        const connection = (await this.getCredentials(
          "astronRpaApi",
        )) as unknown as Connection;
        let next;
        try {
          next = await withMcp(
            connection,
            requests[state.cursor].requestTimeout * 1000,
            (client) =>
              step(
                state,
                requests,
                client,
                Date.now,
                Boolean(this.getNodeParameter("_continue", 0)),
              ),
          );
        } catch (error) {
          next = await step(
            state,
            requests,
            {
              call: async () => {
                throw safeError(error);
              },
            },
            Date.now,
            Boolean(this.getNodeParameter("_continue", 0)),
          );
        }
        return [[{ json: next as unknown as IDataObject }]];
      }
      if (operation === "_result") {
        const keepGoing = Boolean(this.getNodeParameter("_continue", 0));
        return [
          state.results.map((value, index) => {
            if (value.callerError && !keepGoing) {
              throw new NodeOperationError(
                this.getNode(),
                JSON.stringify({
                  code: object(value.callerError).code,
                  ...value,
                }),
                { itemIndex: index },
              );
            }
            if (value.callerError)
              return {
                json: {
                  ...Object.fromEntries(
                    requests[index].inputKeys.map((key) => [key, "[OMITTED]"]),
                  ),
                  ...value,
                },
                error: new NodeOperationError(
                  this.getNode(),
                  JSON.stringify({
                    code: object(value.callerError).code,
                    ...value,
                  }),
                ),
                pairedItem: { item: index },
              };
            return { json: value, pairedItem: { item: index } };
          }),
        ];
      }
      throw new AstronError("INVALID_OPERATION");
    }
    const connection = (await this.getCredentials(
      "astronRpaApi",
    )) as unknown as Connection;
    const output: INodeExecutionData[] = [];
    const requests: Prepared[] = [];
    for (let i = 0; i < inputs.length; i++) {
      let knownExecutionId: string | undefined;
      try {
        if (operation === "getExecution" || operation === "cancelExecution") {
          const value = this.getNodeParameter("executionId", i);
          if (typeof value !== "string" || !executionIdPattern.test(value))
            throw new AstronError("INVALID_EXECUTION_ID");
          knownExecutionId = value;
        }
        const timeout = integer(this, "requestTimeout", i, 3, 120, 15);
        await withMcp(connection, timeout * 1000, async (client) => {
          if (operation === "execute") {
            checkIntegration(await client.call("astron_integration_get", {}));
            const projectId = String(this.getNodeParameter("projectId", i));
            const version = integer(this, "version", i, 1, 2147483647, 1);
            const revision = String(
              this.getNodeParameter("profileRevision", i, ""),
            );
            if (
              revision &&
              !String(this.getNodeParameter("idempotencyKey", i, "")).trim()
            )
              throw new AstronError("RECOVERY_KEY_REQUIRED");
            const profile = revision
              ? { revision }
              : checkWorkflow(
                  await client.call("astron_workflow_get", { projectId }),
                  projectId,
                  version,
                );
            const mode = String(this.getNodeParameter("mode", i, "async"));
            if (!["async", "wait", "sync"].includes(mode))
              throw new AstronError("INVALID_ARGUMENTS");
            const key =
              String(this.getNodeParameter("idempotencyKey", i, "")).trim() ||
              `n8n:${hash([this.getInstanceId(), this.getExecutionId(), this.getNode().id, this.getWorkflowDataProxy(i).$runIndex, i])}`;
            if (key.length > 200) throw new AstronError("INVALID_ARGUMENTS");
            const deadline = integer(this, "executionTimeout", i, 0, 86400, 0);
            const args = {
              projectId,
              version,
              params: jsonObject(this.getNodeParameter("params", i, {})),
              idempotencyKey: key,
              profileRevision: String(profile.revision),
              ...(profile.capabilityClass === "json-data"
                ? { capabilityClass: "json-data" as const }
                : {}),
              ...(deadline ? { executionTimeout: deadline } : {}),
            };
            const fingerprint = hash(args);
            const ctx = this.getContext("node");
            const callKey = `${this.getWorkflowDataProxy(i).$runIndex}:${i}`;
            const fingerprints = (ctx.fingerprints ??= {}) as Record<
              string,
              string
            >;
            if (fingerprints[callKey] && fingerprints[callKey] !== fingerprint)
              throw new AstronError("REQUEST_CHANGED_ON_RETRY");
            fingerprints[callKey] = fingerprint;
            requests.push({
              args,
              mode: mode as Prepared["mode"],
              waitSeconds: Math.min(
                integer(this, "waitSeconds", i, 1, 86400, 300),
                mode === "sync" ? 30 : 86400,
              ),
              pollSeconds: integer(this, "pollSeconds", i, 1, 60, 5),
              requestTimeout: timeout,
              fingerprint,
              keyHash: hash(key),
              itemIndex: i,
              inputKeys: Object.keys(inputs[i].json),
              parentExecutionId: this.getExecutionId(),
            });
          } else if (operation === "listWorkflows") {
            const data = await client.call("astron_workflow_list", {
              offset: integer(this, "offset", i, 0, 2147483647, 0),
              limit: integer(this, "limit", i, 1, 100, 100),
            });
            if (!Array.isArray(data.workflows))
              throw new AstronError("INVALID_RESPONSE");
            output.push({ json: jsonObject(data), pairedItem: { item: i } });
          } else if (operation === "getWorkflow") {
            output.push({
              json: jsonObject(
                await client.call("astron_workflow_get", {
                  projectId: String(this.getNodeParameter("projectId", i)),
                }),
              ),
              pairedItem: { item: i },
            });
          } else if (
            operation === "getExecution" ||
            operation === "cancelExecution"
          ) {
            const executionId = knownExecutionId!;
            const data = snapshot(
              await client.call(
                operation === "getExecution"
                  ? "astron_execution_get"
                  : "astron_execution_cancel",
                { executionId },
              ),
              { executionId },
            );
            output.push({ json: data, pairedItem: { item: i } });
          } else throw new AstronError("INVALID_OPERATION");
        });
      } catch (error) {
        if (operation === "execute") {
          if (!this.continueOnFail())
            throw new NodeOperationError(
              this.getNode(),
              safeError(error).code,
              { itemIndex: i },
            );
          requests.push({
            args: {
              projectId: "",
              version: 1,
              params: {},
              idempotencyKey: "",
              profileRevision: "",
            },
            mode: "async",
            waitSeconds: 1,
            pollSeconds: 1,
            requestTimeout: 15,
            preparationError: safeError(error).code,
            fingerprint: "",
            keyHash: "",
            itemIndex: i,
            inputKeys: Object.keys(inputs[i].json),
            parentExecutionId: this.getExecutionId(),
          });
          continue;
        }
        output.push(
          failure(
            this,
            safeError(error).code,
            knownExecutionId ? { executionId: knownExecutionId } : {},
            i,
            Object.keys(inputs[i].json),
          ),
        );
      }
    }
    if (operation !== "execute" || !requests.length) return [output];
    const result = await this.executeWorkflow(
      { code: runnerWorkflow(this.getNode(), this.continueOnFail()) },
      [{ json: { requests: requests as unknown as IDataObject[] } }],
      undefined,
      {
        parentExecution: {
          executionId: this.getExecutionId(),
          workflowId: this.getWorkflow().id!,
          shouldResume: true,
        },
        executionMode: this.getMode(),
      },
    );
    this.setMetadata({
      subExecution: {
        executionId: result.executionId,
        workflowId: this.getWorkflow().id!,
      },
      subExecutionsCount: 1,
    });
    return result.data.map((items) => items ?? []);
  }
}
