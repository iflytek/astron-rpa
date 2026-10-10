import asyncio
import copy
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from pydantic import SecretStr

PAYLOAD = {
    "instruction": "将工单分为退款或物流；信息不足时不要猜测。",
    "text": "订单重复扣款，请退回多扣的钱。",
    "options": [{"id": "refund", "label": "退款"}, {"id": "shipping", "label": "物流"}],
}


def answer(choice="candidate_0", confidence=0.9):
    return {
        "answers": {
            "selection": {"type": "choice", "choice": choice, "confidence": confidence}
        },
        "model": "jev-1.13.0",
    }


@pytest_asyncio.fixture
async def api():
    from app.config import get_settings
    from app.dependencies import get_user_point_service
    from app.main import app

    state = SimpleNamespace(
        body=answer(),
        status=200,
        error=None,
        delay=0,
        requests=[],
        settings=get_settings().model_copy(
            update={
                "JEV_API_KEY": SecretStr("test-jev-secret"),
                "SEMANTIC_CHOICE_ENABLED": True,
                "SEMANTIC_CHOICE_PROVIDER": "jev",
            }
        ),
        points=SimpleNamespace(
            grant_monthly_points=AsyncMock(),
            get_cached_points=AsyncMock(return_value=10000),
            deduct_points=AsyncMock(),
        ),
    )

    async def upstream(request):
        state.requests.append(request)
        if state.error:
            raise state.error
        if state.delay:
            await asyncio.sleep(state.delay)
        return httpx.Response(state.status, json=state.body)

    app.dependency_overrides[get_settings] = lambda: state.settings
    app.dependency_overrides[get_user_point_service] = lambda: state.points
    async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as provider:
        app.state.decision_http_client = provider
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
            headers={"X-User-Id": "unit-user"},
        ) as client:
            state.client = client
            yield state
    del app.state.decision_http_client
    app.dependency_overrides.clear()


def test_semantic_choice_is_registered_without_jev_credentials():
    from app.main import app

    assert any(route.path == "/v1/decision/choice" for route in app.routes), (
        "The semantic choice node needs a registered decision endpoint"
    )


@pytest.mark.asyncio
async def test_choice_maps_provider_key_to_business_id_and_charges_once(api, caplog):
    import json

    from app.services.point import PointTransactionType

    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 200
    assert response.json() == {
        "status": "matched",
        "selected_id": "refund",
        "confidence": 0.9,
    }
    request = api.requests[0]
    assert str(request.url) == "https://api.typesafe.ai/v1/systemone"
    assert request.headers["Authorization"] == "Bearer test-jev-secret"
    wire = json.loads(request.content)
    assert wire["model"] == "jev-latest"
    assert wire["state"] == {"text": PAYLOAD["text"]}
    assert (
        wire["questions"]["selection"]["criteria"]["candidate_0"]
        == PAYLOAD["options"][0]
    )
    assert "__abstain__" in wire["questions"]["selection"]["criteria"]
    assert len(api.requests) == 1
    api.points.deduct_points.assert_awaited_once_with(
        user_id="unit-user",
        amount=100,
        transaction_type=PointTransactionType.SEMANTIC_CHOICE_COST,
    )
    assert "test-jev-secret" not in caplog.text
    assert PAYLOAD["text"] not in caplog.text


@pytest.mark.asyncio
async def test_explicit_abstention_is_a_completed_billable_decision(api):
    api.body = answer("__abstain__", 1.0)
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.json() == {
        "status": "abstain",
        "selected_id": None,
        "confidence": 1.0,
    }
    api.points.deduct_points.assert_awaited_once()


@pytest.mark.asyncio
async def test_disabled_provider_leaves_other_routes_available(api):
    api.settings.JEV_API_KEY = SecretStr("")
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 503
    assert (await api.client.get("/")).status_code == 200
    assert not api.requests
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_identity_is_rejected_before_inference(api):
    api.client.headers.pop("X-User-Id")
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 401
    assert not api.requests


@pytest.mark.asyncio
async def test_insufficient_points_is_rejected_before_inference(api):
    api.points.get_cached_points.return_value = 0
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 403
    assert not api.requests
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change",
    [
        {"options": []},
        {"options": [{"id": "x", "label": "a"}, {"id": " x ", "label": "b"}]},
        {"options": [{"id": "__abstain__", "label": "a"}]},
        {"options": [{"id": " ", "label": "a"}]},
        {"options": [{"id": "x", "label": " "}]},
        {"options": [{"id": str(n), "label": "a"} for n in range(255)]},
        {"instruction": " "},
        {"text": " "},
        {"text": "a" * 32769},
        {"unexpected": True},
    ],
)
async def test_invalid_input_never_reaches_provider(api, change):
    response = await api.client.post("/v1/decision/choice", json={**PAYLOAD, **change})
    assert response.status_code == 422
    assert not api.requests
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
async def test_maximum_options_reserves_one_slot_for_abstention(api):
    import json

    payload = {
        **PAYLOAD,
        "options": [{"id": str(n), "label": str(n)} for n in range(254)],
    }
    response = await api.client.post("/v1/decision/choice", json=payload)
    assert response.status_code == 200
    assert (
        len(json.loads(api.requests[0].content)["questions"]["selection"]["criteria"])
        == 255
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        {},
        None,
        [],
        {"answers": {"selection": None}},
        answer("unknown"),
        answer(confidence=-0.1),
        answer(confidence=1.1),
        answer(confidence="0.9"),
        answer(confidence=True),
        {
            "answers": {
                "selection": {
                    "type": "score",
                    "choice": "candidate_0",
                    "confidence": 0.9,
                }
            }
        },
        {"answers": {"selection": {"type": "choice", "choice": "candidate_0"}}},
    ],
)
async def test_malformed_provider_answer_is_error_not_abstention(api, body):
    api.body = copy.deepcopy(body)
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 502
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["jev", "openai_compatible"])
@pytest.mark.parametrize("status", [401, 422, 429, 500, 529])
async def test_provider_errors_do_not_leak_details_or_charge(api, status, provider):
    api.settings.SEMANTIC_CHOICE_PROVIDER = provider
    api.status = status
    api.body = {"error": "test-jev-secret confidential upstream message"}
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 502
    assert "confidential" not in response.text
    assert "test-jev-secret" not in response.text
    assert len(api.requests) == 1
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error,status",
    [(httpx.ReadTimeout("secret"), 504), (httpx.ConnectError("secret"), 502)],
)
async def test_transport_failure_never_becomes_abstention(api, error, status):
    api.error = error
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == status
    assert "secret" not in response.text
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
async def test_total_inference_deadline(api):
    api.delay = 1
    api.settings.SEMANTIC_CHOICE_TIMEOUT_SECONDS = 0.01
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 504
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
async def test_lifespan_reuses_and_closes_provider_client(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "create_db_and_tables", AsyncMock())
    monkeypatch.setattr(main, "init_redis_pool", AsyncMock())
    close_redis = AsyncMock()
    monkeypatch.setattr(main, "close_redis_pool", close_redis)
    async with main.lifespan(main.app):
        client = main.app.state.decision_http_client
        assert not client.is_closed
        assert main.app.state.decision_http_client is client
    assert client.is_closed
    close_redis.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "choice,status,selected",
    [("candidate_0", "matched", "refund"), ("__abstain__", "abstain", None)],
)
async def test_engine_component_through_real_decision_route(
    api, monkeypatch, choice, status, selected
):
    import importlib.util
    import sys
    from pathlib import Path
    from types import ModuleType

    # Only the desktop runtime and its local HTTP gateway are replaced; the
    # engine method, ASGI route, provider mapping and billing logic are real.
    atomic = ModuleType("astronverse.actionlib.atomic")
    atomic.atomicMg = SimpleNamespace(
        atomic=lambda *args, **kwargs: lambda fn: fn,
        param=lambda *args, **kwargs: None,
        cfg=lambda: {"GATEWAY_PORT": 13159},
    )
    monkeypatch.setitem(sys.modules, "astronverse.actionlib.atomic", atomic)
    monkeypatch.setitem(sys.modules, "requests", ModuleType("requests"))
    repo = Path(__file__).resolve().parents[4]
    path = repo / "engine/components/astronverse-ai/src/astronverse/ai/semantic.py"
    spec = importlib.util.spec_from_file_location("semantic_flow_test", path)
    component = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(component)
    loop = asyncio.get_running_loop()

    def gateway(url, json, timeout):
        assert url == "http://127.0.0.1:13159/api/rpa-ai-service/v1/decision/choice"
        response = asyncio.run_coroutine_threadsafe(
            api.client.post("/v1/decision/choice", json=json), loop
        ).result(timeout=5)
        return httpx.Response(
            response.status_code, content=response.content, request=response.request
        )

    monkeypatch.setattr(component.requests, "post", gateway, raising=False)
    api.body = answer(choice)
    result = await asyncio.to_thread(component.SemanticAI.choose, **PAYLOAD)
    assert result == {"status": status, "selected_id": selected, "confidence": 0.9}
    api.points.deduct_points.assert_awaited_once()


def test_generic_configuration_defaults():
    from app.config import get_settings
    from app.schemas.chat import DEFAULT_MODEL

    settings = get_settings()
    assert settings.SEMANTIC_CHOICE_ENABLED is False
    assert settings.SEMANTIC_CHOICE_PROVIDER == "openai_compatible"
    assert settings.SEMANTIC_CHOICE_MODEL == DEFAULT_MODEL


@pytest.mark.asyncio
async def test_capabilities_explain_disabled_configuration_without_billing(api):
    api.settings = api.settings.model_copy(update={"SEMANTIC_CHOICE_ENABLED": False})
    response = await api.client.get("/v1/decision/capabilities")
    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "reason": "Set SEMANTIC_CHOICE_ENABLED=true to enable semantic choice",
    }
    api.points.get_cached_points.assert_not_awaited()
    assert not api.requests


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "choice,selected", [("candidate_1", "shipping"), ("__abstain__", None)]
)
async def test_openai_structured_choice_uses_existing_credentials(
    api, choice, selected
):
    import json

    api.settings.SEMANTIC_CHOICE_PROVIDER = "openai_compatible"
    api.body = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps({"choice": choice})},
            }
        ]
    }
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 200
    assert response.json() == {
        "status": "matched" if selected else "abstain",
        "selected_id": selected,
        "confidence": None,
    }
    request = api.requests[0]
    assert str(request.url) == "https://chat.invalid/v1/chat/completions"
    assert request.headers["Authorization"] == "Bearer unit"
    wire = json.loads(request.content)
    assert wire["model"] == api.settings.SEMANTIC_CHOICE_MODEL
    schema = wire["response_format"]["json_schema"]
    assert schema["strict"] is True
    assert schema["schema"]["properties"]["choice"]["enum"] == [
        "candidate_0",
        "candidate_1",
        "__abstain__",
    ]
    assert json.loads(wire["messages"][1]["content"])["text"] == PAYLOAD["text"]
    api.points.deduct_points.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message,finish",
    [
        ({"content": '{"choice":"unknown"}'}, "stop"),
        ({"content": '```json\n{"choice":"candidate_0"}\n```'}, "stop"),
        ({"content": '{"choice":"candidate_0", "confidence":0.9}'}, "stop"),
        ({"content": '{"choice":"candidate_0"}'}, "length"),
        ({"content": '{"choice":"candidate_0"}', "refusal": "Cannot answer"}, "stop"),
        ({"content": None}, "stop"),
        (None, "stop"),
        ([], "stop"),
        ("invalid", "stop"),
    ],
)
async def test_invalid_openai_output_is_not_billed_or_retried(api, message, finish):
    api.settings.SEMANTIC_CHOICE_PROVIDER = "openai_compatible"
    api.body = {"choices": [{"finish_reason": finish, "message": message}]}
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 502
    assert len(api.requests) == 1
    api.points.deduct_points.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider,variable",
    [
        ("jev", "JEV_API_KEY"),
        ("jev", "JEV_MODEL"),
        ("openai_compatible", "AICHAT_API_KEY"),
        ("openai_compatible", "AICHAT_BASE_URL"),
        ("openai_compatible", "SEMANTIC_CHOICE_MODEL"),
    ],
)
async def test_capability_and_execution_report_missing_variable(
    api, provider, variable
):
    api.settings.SEMANTIC_CHOICE_PROVIDER = provider
    setattr(
        api.settings, variable, SecretStr(" ") if variable == "JEV_API_KEY" else " "
    )
    readiness = await api.client.get("/v1/decision/capabilities")
    assert readiness.status_code == 200
    assert readiness.json()["enabled"] is False
    assert variable in readiness.json()["reason"]
    response = await api.client.post("/v1/decision/choice", json=PAYLOAD)
    assert response.status_code == 503
    assert response.json()["detail"] == readiness.json()["reason"]
    assert not api.requests
    api.points.get_cached_points.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["jev", "openai_compatible"])
async def test_enabled_capability_does_not_probe_or_bill(api, provider):
    api.settings.SEMANTIC_CHOICE_PROVIDER = provider
    response = await api.client.get("/v1/decision/capabilities")
    assert response.json() == {"enabled": True, "reason": None}
    assert not api.requests
    api.points.get_cached_points.assert_not_awaited()
    api.client.headers.pop("X-User-Id")
    assert (await api.client.get("/v1/decision/capabilities")).json() == {
        "enabled": True,
        "reason": None,
    }
