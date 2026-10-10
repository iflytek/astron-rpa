# Semantic choice

The **AI语义判断 → 语义选择** component selects a stable option ID from text,
or explicitly abstains. Existing workflow conditions decide what to do next.
It uses the authenticated desktop gateway and `POST /v1/decision/choice`.

## Enable and publish

The feature is disabled by default. Configure the existing OpenAI-compatible
service in `docker/.env`, then enable semantic choice:

```dotenv
AICHAT_BASE_URL=https://your-provider.example/v1
AICHAT_API_KEY=your-server-key
SEMANTIC_CHOICE_ENABLED=true
SEMANTIC_CHOICE_PROVIDER=openai_compatible
SEMANTIC_CHOICE_MODEL=maas/deepseek-v3.2
SEMANTIC_CHOICE_TIMEOUT_SECONDS=10
SEMANTIC_CHOICE_POINTS_COST=100
```

Set the model to a model your service supports. It must support strict
`response_format.type=json_schema` output. Compatibility with chat completions
alone does not establish this capability. Unsupported structured output,
refusals, truncated responses and invalid output fail explicitly; there is no
fallback to free-text parsing, another provider, or another paid attempt.

The timeout must be positive and at most 30 seconds; the point cost must be
positive. Keep credentials on the server. The robot service runs a compiled image, so recreating its existing container
alone does not install this Java change. From the repository root, build this
revision and use a Compose override (or deploy a released image containing it):

```sh
docker build -f backend/robot-service/Dockerfile -t astron-robot-semantic:local .
cat > docker/compose.semantic.local.yml <<'YAML'
services:
  robot-service:
    image: astron-robot-semantic:local
YAML
cd docker
docker compose -f docker-compose.yml -f compose.semantic.local.yml up -d --force-recreate ai-service robot-service openresty-nginx
```

Keep this local deployment override outside commits. On later configuration
changes, use the same Compose files when recreating services. The AI service
source and gateway Lua are mounted by the supplied Compose configuration.
For non-Compose deployments, the robot service capability URL can be set with
`AI_SERVICE_DECISION_CAPABILITIES_URL`; its default is
`http://ai-service:8010/v1/decision/capabilities`.

For a fresh database, initialization publishes the metadata. For an existing
database, take your normal backup and apply the additive migration:

```sh
docker compose exec -T mysql sh -c \
  'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4' \
  < migrations/20260923_add_semantic_choice.sql
```

Rebuild/install the client from this revision and reopen the designer.
Metadata alone does not update an installed engine. The service owns readiness:
`GET /v1/decision/capabilities` returns `{ "enabled": false, "reason": "..." }`
or `{ "enabled": true, "reason": null }`. It checks configuration, not provider
reachability or model quality, and never makes a paid call.

When unavailable, the component tree hides this node. Its definition remains
available so saved workflows can open; the designer warns about unavailable
semantic nodes, and execution reports the configuration variable to change.
Other nodes remain available if the capability service cannot be reached.

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
{"status": "matched", "selected_id": "refund", "confidence": null}
```

An explicit model abstention returns:

```json
{"status": "abstain", "selected_id": null, "confidence": null}
```

- Supply 1–254 options with unique, nonempty IDs; `__abstain__` is reserved by
  this integration for the additional refusal option, not a native provider token.
- Strings are trimmed; maximum lengths are 2,048 characters for instruction,
  32,768 for text, 128 for IDs, and 512 for labels.
- Valid decisions, including abstentions, consume `SEMANTIC_CHOICE_POINTS_COST` points
  under the existing `semantic_choice_cost` transaction category, after inference.
- Invalid input (422), missing identity (401), insufficient points (403),
  disabled integration (503), provider timeout (504), and provider/protocol
  errors (502) are errors; provider failures do not deduct points.
- The component propagates errors to normal workflow exception handling; it
  does not silently convert a failure into abstention or retry paid inference.
- Only the supplied text and candidate descriptions go to the configured provider; minimize
  business data in these inputs. The adapter does not log the payload or key.

The OpenAI-compatible provider returns `confidence: null`: model-generated
self-assessments are not treated as calibrated confidence. Workflow expressions
must check for null before using confidence thresholds. Existing option IDs and
matched/abstain semantics remain unchanged.

Character limits do not guarantee that a request fits a provider's token budget.
Keep descriptions concise and evaluate classification on representative data.
For the optional provider, see [provider configuration](JEV_SEMANTIC_CHOICE.md).

## Verification

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
the real FastAPI decision router, identity dependency, point checker and OpenAI-compatible
adapter. Only the remote authentication service, provider transport and points store
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
published on a random loopback port. The 15 cases cover token and session-cookie
identity forwarding despite spoofed headers, credential rejection without
inference or charging, matched and abstained results, provider failures and
selection of the unchanged sibling AI route. This is an HTTP route smoke test;
it does not validate the deployment's TLS certificates or live model quality.

The identity policy also has an offline Lua/LuaJIT check with mocked gateway
and authentication-service boundaries: `lua docker/tests/decision_auth_spec.lua`.

These tests establish protocol and error-handling behavior, not model quality
or speed. For a live comparison, run the same labeled Chinese tickets through
the configured providers, recording accuracy, abstention rate, decision and
whole-workflow P50/P95 latency, and cost; do not infer workflow speed from
provider latency alone.
