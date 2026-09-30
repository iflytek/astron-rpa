# Semantic choice with Jev

The **AI语义判断 → 语义选择** component classifies text against a supplied list
of options. It returns a stable option ID or an explicit abstention. It does
not generate text, inspect screenshots, choose browser coordinates, or perform
an action. Use existing workflow conditions to act on its result.

The component calls the local authenticated gateway, which forwards to
`POST /v1/decision/choice` in `ai-service`. The service calls TypeSafe's
[System One HTTP API](https://docs.typesafe.ai/api) with one `Choice` question.
No TypeSafe SDK or additional client dependency is required.

## Enable the service and publish the component

1. In `docker/.env`, configure a server-owned credential:

   ```dotenv
   JEV_API_KEY=your-typesafe-api-key
   JEV_MODEL=jev-latest
   JEV_TIMEOUT_SECONDS=10
   JEV_POINTS_COST=100
   ```

   An empty key disables this endpoint with HTTP 503 and leaves existing AI
   features available. The inference timeout must be greater than zero and at
   most 30 seconds; the point cost must be a positive integer. Do not put the
   key in workflow variables, component metadata, or browser extensions.

2. Update the server source and recreate the AI service and gateway from
   `docker/`:

   ```sh
   docker compose up -d --force-recreate ai-service openresty-nginx
   ```

   Keep the AI service on the private container network. The new decision
   route requires a desktop session and discards caller-supplied identity
   headers; a TypeSafe key is not an AstronRPA login credential.

3. For a **new database**, the initialization SQL includes the node and its
   category. For an **existing database**, apply only the incremental migration
   from `docker/` after taking your normal database backup:

   ```sh
   docker compose exec -T mysql sh -c \
     'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4' \
     < migrations/20260923_add_semantic_choice.sql
   ```

   The migration targets the repository's `rpa` schema. It can be repeated,
   adds missing metadata, and preserves existing custom nodes and categories.
   Do not rerun the full initialization script against an existing database.

4. Rebuild/install the client from this revision using `BUILD_GUIDE.md`, then
   reopen the process designer to refresh its component list. Both the engine
   implementation and the server metadata are needed; publishing metadata
   alone does not update an installed client.

## Example: route a support ticket

1. Read a ticket's text with the existing browser component, or use the text
   `订单重复扣款，请退回多扣的钱。`.
2. Create a List variable containing:

   ```python
   [
       {"id": "refund", "label": "退款、重复扣款、退回费用"},
       {"id": "shipping", "label": "物流、配送进度、未收到包裹"},
       {"id": "invoice", "label": "发票开具或修改"},
       {"id": "other", "label": "明确属于其他客服事项"},
   ]
   ```

3. Add **语义选择**, set **判断说明** to
   `按工单主要诉求分类；信息不足或不属于客服事项时不要猜测。`, reference the
   ticket in **待判断文本**, and reference the List in **候选列表**.
4. Save the output as `semantic_result` and branch on its fields:
   - `semantic_result["status"] == "abstain"`: route for manual review.
   - `semantic_result["selected_id"] == "refund"`: enter the refund-handling
     workflow, including its existing business checks.
   - Handle the other IDs in their corresponding branches.

For this example, `refund` is the expected classification, not a guaranteed
model result. A domain label such as `other` is different from abstention.
Confidence describes the model's choice certainty, not verified accuracy;
evaluate thresholds on your own samples before using decisions for actions.

## API contract

```json
{
  "instruction": "按工单主要诉求分类；信息不足时不要猜测。",
  "text": "订单重复扣款，请退回多扣的钱。",
  "options": [
    {"id": "refund", "label": "退款"},
    {"id": "shipping", "label": "物流"}
  ]
}
```

The response is a plain object, without a `data` envelope:

```json
{"status": "matched", "selected_id": "refund", "confidence": 0.9}
```

An explicit model abstention returns:

```json
{"status": "abstain", "selected_id": null, "confidence": 0.9}
```

- Supply 1–254 options with unique, nonempty IDs; `__abstain__` is reserved by
  this integration for the additional refusal option, not a native Jev token.
- Strings are trimmed; maximum lengths are 2,048 characters for instruction,
  32,768 for text, 128 for IDs, and 512 for labels.
- Valid decisions, including abstentions, consume `JEV_POINTS_COST` points
  under the existing `aichat_cost` transaction category, after inference.
- Invalid input (422), missing identity (401), insufficient points (403),
  disabled integration (503), provider timeout (504), and provider/protocol
  errors (502) are errors; provider failures do not deduct points.
- The component propagates errors to normal workflow exception handling; it
  does not silently convert a failure into abstention or retry paid inference.
- Only the supplied text and candidate descriptions go to TypeSafe; minimize
  business data in these inputs. The adapter does not log the payload or key.

## Verification

### Differences from the official quick start

The [quick start](https://docs.typesafe.ai/introduction/quickstart) uses the
SDK defaults. This integration uses the documented HTTP API directly:

- `JEV_API_KEY` is this service's configuration name for the same TypeSafe
  credential that the SDK reads as `TYPESAFE_API_KEY`.
- The default uses `jev-latest`, matching the official quick start. This
  alias follows stable releases, so model behavior can change when TypeSafe
  updates it. The [models page](https://docs.typesafe.ai/models) describes
  available versions; administrators can pin `JEV_MODEL` if required.
- Object-valued `state` and candidate descriptions are supported by the
  API. Internal candidate keys map back to the supplied workflow option IDs.
- The workflow result exposes only the selected ID and confidence. The
  provider also returns `probabilities`, resolved `model`, and token `usage`;
  these are not exposed by this component. Confidence is not the winning
  option's probability.
- The official SDK retries rate limits and overload responses with backoff.
  This component makes one attempt within its deadline; provider 429/529
  responses become workflow errors (502), with no automatic retry.
- Input character limits are application bounds, not a guarantee that a
  request fits the model's token budget. Jev 1.13 limits the state plus the
  longest question to 32k tokens; large candidate lists can exceed this even
  when each individual field is valid. Shorten inputs or classify in stages.

The official models page identifies English as the strongest language and
recommends evaluating other languages on actual workload data. Chinese
examples here demonstrate wiring, not measured Chinese classification quality.

### Offline checks

Offline backend tests use the real ASGI routes with a mock provider transport
and point service; they need neither model credentials nor MySQL/Redis:

```sh
cd backend/ai-service
uv run pytest --confcutdir=tests/unit tests/unit -q
```

Engine tests mock the atomic runtime and HTTP boundary and execute the actual
component method:

```sh
uv run --project engine pytest engine/components/astronverse-ai/tests -q
```

Gateway identity regressions run in disposable Docker containers:

```sh
sh docker/tests/test-auth-handler.sh
```

The production-route smoke test loads the complete production gateway route
include and real authentication Lua in OpenResty, then proxies HTTP requests to
the real FastAPI decision router, identity dependency, point checker and Jev
adapter. Only the remote authentication service, Jev transport and points store
are mocked; no credentials or paid API are needed:

```sh
# Prerequisites: Docker, the ai-service Python environment, and the cached image.
docker pull openresty/openresty:1.27.1.1-alpine
backend/ai-service/.venv/bin/python docker/tests/test-semantic-choice-gateway.py
```

`OPENRESTY_IMAGE` can select another locally cached OpenResty image. The script
creates a disposable Docker network and containers and removes them on exit.
Its temporary host HTTP listener binds all interfaces so Docker Desktop and
Linux Docker can reach it; it serves synthetic fixtures only. The gateway is
published on a random loopback port. The 12 cases cover token and session-cookie
identity forwarding despite spoofed headers, credential rejection without
inference or charging, matched and abstained results, provider failures and
selection of the unchanged sibling AI route. This is an HTTP route smoke test;
it does not validate the deployment's TLS certificates or live model quality.

The identity policy also has an offline Lua/LuaJIT check with mocked gateway
and authentication-service boundaries: `lua docker/tests/decision_auth_spec.lua`.

These tests establish protocol and error-handling behavior, not model quality
or speed. For a live comparison, run the same labeled Chinese tickets through
the existing model and Jev, recording accuracy, abstention rate, decision and
whole-workflow P50/P95 latency, and cost; do not infer workflow speed from
provider latency alone.
