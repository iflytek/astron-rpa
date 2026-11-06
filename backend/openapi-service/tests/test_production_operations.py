import asyncio
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette.responses import StreamingResponse

from app.middlewares.tracing import RequestTracingMiddleware, correlation_ctx, get_request_id
from app.routers.healthcheck import monitoring_authorized
from app.security import integration_rate_limit as limiter
from app.services import observability as metrics


@pytest.mark.asyncio
async def test_streaming_correlation_is_scoped_and_not_buffered():
    seen = []

    async def app(scope, receive, send):
        async def body():
            seen.append((get_request_id(), correlation_ctx.get().copy()))
            yield b"event: message\n"
            await asyncio.sleep(0)
            seen.append((get_request_id(), correlation_ctx.get().copy()))
            yield b"data: {}\n\n"

        await StreamingResponse(body(), media_type="text/event-stream")(scope, receive, send)

    async def call(identifier):
        sent = []
        scope = {
            "type": "http",
            "asgi": {"spec_version": "2.4"},
            "method": "POST",
            "path": "/mcp/",
            "headers": [
                (b"x-request-id", identifier.encode()),
                (b"x-n8n-execution-id", b"123"),
                (b"x-n8n-item-index", b"0"),
            ],
        }
        await RequestTracingMiddleware(app)(scope, AsyncMock(), AsyncMock(side_effect=sent.append))
        assert get_request_id() is None
        assert correlation_ctx.get() is None
        assert (b"x-request-id", identifier.encode()) in sent[0]["headers"]
        assert sent[1]["body"] == b"event: message\n"
        assert sent[2]["body"] == b"data: {}\n\n"

    await asyncio.gather(call("first"), call("second"))
    assert [row[0] for row in seen].count("first") == 2
    assert [row[0] for row in seen].count("second") == 2
    assert all(row[1] == {"n8n_execution_id": "123", "n8n_item_index": "0"} for row in seen)


@pytest.mark.asyncio
async def test_invalid_trace_and_cancelled_response_reset_context():
    async def app(scope, receive, send):
        assert len(get_request_id()) == 32
        assert correlation_ctx.get()["n8n_execution_id"] is None
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await RequestTracingMiddleware(app)(
            {
                "type": "http",
                "path": "/mcp/",
                "headers": [(b"x-request-id", b"bad\nvalue"), (b"x-n8n-execution-id", b"x" * 200)],
            },
            AsyncMock(),
            AsyncMock(),
        )
    assert get_request_id() is None
    assert correlation_ctx.get() is None


def test_structured_logs_omit_exception_payload_and_redact_secrets():
    record = logging.LogRecord(
        "test",
        logging.ERROR,
        __file__,
        1,
        "Authorization: Bearer secret",
        (),
        (ValueError, ValueError("private-result"), None),
    )
    result = json.loads(metrics.JsonFormatter().format(record))
    assert result["exception_type"] == "ValueError"
    assert "secret" not in json.dumps(result)
    assert "private-result" not in json.dumps(result)
    assert result["pid"] > 0


def test_metrics_have_bounded_labels_and_histogram_buckets(monkeypatch):
    from collections import Counter

    monkeypatch.setattr(metrics, "_counts", Counter())
    monkeypatch.setattr(metrics, "event", lambda *a, **kw: None)
    for i in range(200):
        metrics.http_observed({"path": f"/executions/private-{i}?secret=example"}, 200, 0.25)
    metrics.http_observed({"path": "/health/metrics"}, 200, 1)
    metrics.execution_transition("COMPLETED")
    output = metrics.render_metrics(2)
    assert "private" not in output
    assert "secret" not in output
    assert 'astron_http_requests_total{route="rest",status="2xx"} 200' in output
    assert 'astron_http_duration_seconds_bucket{route="rest",le="+Inf"} 200' in output
    assert "astron_clients_online 2" in output
    assert len(metrics._counts) <= 13


def test_monitoring_requires_separate_nonempty_token(monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    for token in ("", "short", "a" * 32):
        monkeypatch.setattr(settings, "MONITORING_TOKEN", token)
        for supplied in (None, "Bearer user-api-key", "Bearer " + "b" * 32):
            with pytest.raises(HTTPException) as error:
                monitoring_authorized(supplied)
            assert error.value.status_code == 404
    monitoring_authorized("Bearer " + "a" * 32)


@pytest.mark.asyncio
async def test_shared_limit_denies_before_dispatch_and_fails_closed(monkeypatch):
    from app import redis as redis_module

    monkeypatch.setattr(limiter, "get_settings", lambda: SimpleNamespace(INTEGRATION_RATE_PER_MINUTE=2))
    monkeypatch.setattr(redis_module, "redis_pool", object())
    client = SimpleNamespace(eval=AsyncMock(side_effect=[[1, 60], [2, 59], [3, 58], OSError("private")]))
    monkeypatch.setattr(limiter, "Redis", lambda **kw: client)
    await limiter.enforce_rate_limit("owner")
    await limiter.enforce_rate_limit("owner")
    with pytest.raises(HTTPException) as rejected:
        await limiter.enforce_rate_limit("owner")
    assert rejected.value.status_code == 429
    assert rejected.value.headers == {"Retry-After": "58"}
    with pytest.raises(HTTPException) as unavailable:
        await limiter.enforce_rate_limit("owner")
    assert unavailable.value.status_code == 503
    assert "private" not in str(unavailable.value.detail)
    assert "owner" not in client.eval.call_args.args[2]


@pytest.mark.asyncio
async def test_disabled_limit_has_no_redis_dependency(monkeypatch):
    monkeypatch.setattr(limiter, "get_settings", lambda: SimpleNamespace(INTEGRATION_RATE_PER_MINUTE=0))
    monkeypatch.setattr(limiter, "Redis", lambda **kw: pytest.fail("Redis should not be used"))
    await limiter.enforce_rate_limit("owner")


@pytest.mark.asyncio
@pytest.mark.parametrize("healthy", [True, False])
async def test_metrics_report_dependency_readiness(monkeypatch, healthy):
    from app import dependencies
    from app.routers import healthcheck

    manager = SimpleNamespace(router=SimpleNamespace(local={"synthetic": object()}))
    monkeypatch.setattr(dependencies, "get_ws_service", AsyncMock(return_value=SimpleNamespace(ws_manager=manager)))
    probe = AsyncMock(side_effect=None if healthy else HTTPException(503, "not ready"))
    monkeypatch.setattr(healthcheck, "ready", probe)
    response = await healthcheck.metrics()
    assert response.status_code == 200
    assert f"astron_ready {int(healthy)}\n" in response.body.decode()
    assert "astron_clients_online 1\n" in response.body.decode()
    probe.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("failed", [None, "sql", "redis", "router"])
async def test_readiness_checks_each_required_dependency(monkeypatch, failed):
    from redis import asyncio as redis_asyncio

    from app import database, dependencies
    from app import redis as redis_module
    from app.routers.healthcheck import ready

    db = SimpleNamespace(execute=AsyncMock(side_effect=OSError("private") if failed == "sql" else None))
    session = AsyncMock()
    session.__aenter__.return_value = db
    monkeypatch.setattr(database, "AsyncSessionLocal", lambda: session)
    monkeypatch.setattr(redis_module, "redis_pool", object())
    broker = SimpleNamespace(ping=AsyncMock(side_effect=OSError("private") if failed == "redis" else None))
    monkeypatch.setattr(redis_asyncio, "Redis", lambda **kw: broker)
    manager = SimpleNamespace(router=SimpleNamespace(ready=failed != "router"))
    monkeypatch.setattr(dependencies, "get_ws_service", AsyncMock(return_value=SimpleNamespace(ws_manager=manager)))
    if failed:
        with pytest.raises(HTTPException) as rejected:
            await ready()
        assert rejected.value.status_code == 503
        assert "private" not in str(rejected.value.detail)
    else:
        assert await ready() == {"ready": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("routing", ["local", "redis"])
async def test_discovery_reports_the_configured_topology(monkeypatch, routing):
    from app.services import workflow_control

    monkeypatch.setattr(workflow_control, "get_settings", lambda: SimpleNamespace(EXECUTION_ROUTING=routing))
    monkeypatch.setattr(workflow_control.management, "capabilities", AsyncMock(return_value={"supportsCancel": True}))
    result = await workflow_control.WorkflowControlService(None).get_integration("synthetic-owner")
    assert result["client"]["state"] == "ready"
    assert ("single-openapi-owner" in result["limitations"]) == (routing == "local")
    assert ("same-host-shared-storage" in result["limitations"]) == (routing == "redis")
    assert "controlled-validation" in result["limitations"]
