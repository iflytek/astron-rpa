import type { INode, IWorkflowBase } from "n8n-workflow";

/** Node-owned orchestration through the public inline-subworkflow API. */
export function runnerWorkflow(
  parent: INode,
  continueOnFail: boolean,
): IWorkflowBase {
  const internal = (name: string, operation: string, x: number): INode => ({
    id: name,
    name,
    type: parent.type,
    typeVersion: parent.typeVersion,
    position: [x, 0],
    credentials: parent.credentials,
    parameters: {
      operation,
      _requests: "={{ $('Input').first().json.requests }}",
      _continue: continueOnFail,
      _resumeState: "={{ $json }}",
    },
  });
  const link = (node: string) => ({ node, type: "main" as const, index: 0 });
  return {
    name: "AstronRPA managed execution",
    active: false,
    isArchived: false,
    nodes: [
      {
        id: "input",
        name: "Input",
        type: "n8n-nodes-base.executeWorkflowTrigger",
        typeVersion: 1.1,
        position: [0, 0],
        parameters: { inputSource: "passthrough" },
      },
      internal("State", "_state", 200),
      internal("Checkpoint", "_pause", 400),
      internal("Observe", "_step", 600),
      internal("Pause", "_pause", 1000),
      internal("Result", "_result", 1200),
      {
        id: "pending",
        name: "Pending",
        type: "n8n-nodes-base.if",
        typeVersion: 2.2,
        position: [800, 0],
        parameters: {
          conditions: {
            options: {
              caseSensitive: true,
              leftValue: "",
              typeValidation: "strict",
              version: 2,
            },
            conditions: [
              {
                id: "pending",
                leftValue: "={{ $json.done }}",
                rightValue: "",
                operator: {
                  type: "boolean",
                  operation: "false",
                  singleValue: true,
                },
              },
            ],
            combinator: "and",
          },
          options: {},
        },
      },
    ],
    connections: {
      Input: { main: [[link("State")]] },
      State: { main: [[link("Checkpoint")]] },
      Checkpoint: { main: [[link("Observe")]] },
      Observe: { main: [[link("Pending")]] },
      Pending: { main: [[link("Pause")], [link("Result")]] },
      Pause: { main: [[link("Observe")]] },
    },
    settings: {
      executionOrder: "v1",
      saveDataSuccessExecution: "all",
      saveDataErrorExecution: "all",
    },
  } as unknown as IWorkflowBase;
}
