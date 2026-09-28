import { createHash } from "node:crypto";
import type { IDataObject } from "n8n-workflow";
import {
  AstronError,
  checkIntegration,
  object,
  snapshot,
  type Snapshot,
} from "../mapping/contracts";
import type { McpConnection } from "../transport/mcp";
import { safeError } from "../transport/mcp";

export function hash(value: unknown): string {
  const canonical = (v: unknown): unknown =>
    Array.isArray(v)
      ? v.map(canonical)
      : v && typeof v === "object"
        ? Object.fromEntries(
            Object.entries(v)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([k, v]) => [k, canonical(v)]),
          )
        : v;
  return createHash("sha256")
    .update(JSON.stringify(canonical(value)))
    .digest("hex");
}
export interface Prepared {
  args: {
    projectId: string;
    version: number;
    params: IDataObject;
    idempotencyKey: string;
    profileRevision: string;
    capabilityClass?: "json-data";
    executionTimeout?: number;
  };
  mode: "async" | "wait" | "sync";
  waitSeconds: number;
  pollSeconds: number;
  requestTimeout: number;
  fingerprint: string;
  keyHash: string;
  itemIndex: number;
  inputKeys: string[];
  parentExecutionId: string;
  preparationError?: string;
}
export interface Active {
  deadline: number;
  attempts: number;
  snapshot?: Snapshot;
}
export interface RunState {
  format: 1;
  cursor: number;
  active: Active;
  results: IDataObject[];
  done: boolean;
  nextPoll: number;
}
export function initialState(requests: Prepared[], now: number): RunState {
  return {
    format: 1,
    cursor: 0,
    active: { deadline: now + requests[0].waitSeconds * 1000, attempts: 0 },
    results: [],
    done: false,
    nextPoll: now + 1000,
  };
}
export function stateFrom(value: unknown, size: number): RunState {
  const v = object(value);
  if (
    v.format !== 1 ||
    !Number.isInteger(v.cursor) ||
    Number(v.cursor) < 0 ||
    Number(v.cursor) > size ||
    !Array.isArray(v.results) ||
    typeof v.done !== "boolean" ||
    !Number.isFinite(v.nextPoll) ||
    !Number.isFinite(object(v.active).deadline) ||
    !Number.isInteger(object(v.active).attempts)
  ) {
    throw new AstronError("RESUME_CONTEXT_UNSUPPORTED");
  }
  return structuredClone(v) as unknown as RunState;
}
function envelope(
  req: Prepared,
  state: RunState,
  errorCode?: string,
): IDataObject {
  return {
    ...(state.active.snapshot ?? {
      projectId: req.args.projectId,
      version: req.args.version,
    }),
    correlation: {
      n8nExecutionId: req.parentExecutionId,
      itemIndex: req.itemIndex,
      keyHash: req.keyHash,
      requestFingerprint: req.fingerprint,
      profileRevision: req.args.profileRevision,
    },
    ...(errorCode
      ? { callerError: { code: errorCode, message: errorCode } }
      : {}),
  };
}

/** One bounded observation. State contains no credentials or request parameter copies. */
export async function step(
  state: RunState,
  requests: Prepared[],
  client: Pick<McpConnection, "call">,
  now: () => number = Date.now,
  continueOnFail = false,
): Promise<RunState> {
  if (state.done) return state;
  const req = requests[state.cursor];
  let failure: string | undefined;
  let unresolved = false;
  try {
    if (req.preparationError) throw new AstronError(req.preparationError);
    if (req.mode !== "async" && now() >= state.active.deadline) {
      failure = "WAIT_BUDGET_EXPIRED";
      unresolved = state.active.snapshot
        ? !state.active.snapshot.terminal
        : state.active.attempts > 0;
    } else if (state.active.snapshot) {
      state.active.snapshot = snapshot(
        await client.call("astron_execution_get", {
          executionId: state.active.snapshot.executionId,
        }),
        {
          executionId: state.active.snapshot.executionId,
          projectId: req.args.projectId,
          version: req.args.version,
        },
      );
    } else {
      checkIntegration(await client.call("astron_integration_get", {}));
      state.active.attempts++;
      state.active.snapshot = snapshot(
        await client.call("astron_workflow_execute", req.args),
        { projectId: req.args.projectId, version: req.args.version },
      );
    }
    const current = state.active.snapshot;
    if (current?.terminal && current.status !== "succeeded")
      failure = String(
        object(current.error ?? { code: "EXECUTION_CANCELLED" }).code,
      );
    if (!failure && current && !current.terminal && req.mode !== "async") {
      if (now() < state.active.deadline) {
        state.nextPoll = Math.min(
          now() + req.pollSeconds * 1000,
          state.active.deadline,
        );
        return state;
      }
      failure = "WAIT_BUDGET_EXPIRED";
      unresolved = true;
    }
  } catch (error) {
    const safe = safeError(error);
    unresolved =
      safe.uncertain ||
      (!!state.active.snapshot && !state.active.snapshot.terminal);
    if (
      safe.uncertain &&
      now() < state.active.deadline &&
      (state.active.snapshot || state.active.attempts < 2)
    ) {
      state.nextPoll = Math.min(
        now() + req.pollSeconds * 1000,
        state.active.deadline,
      );
      return state;
    }
    failure = safe.code;
  }
  state.results.push(envelope(req, state, failure));
  state.cursor++;
  if (unresolved || (failure && !continueOnFail)) {
    for (; state.cursor < requests.length; state.cursor++) {
      state.results.push(
        envelope(
          requests[state.cursor],
          { ...state, active: { deadline: 0, attempts: 0 } },
          "PREVIOUS_EXECUTION_UNRESOLVED",
        ),
      );
    }
  }
  state.done = state.cursor === requests.length;
  if (!state.done) {
    state.active = {
      deadline: now() + requests[state.cursor].waitSeconds * 1000,
      attempts: 0,
    };
    state.nextPoll = now() + 1000;
  }
  return state;
}
