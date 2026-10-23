"""Caller-level compatibility through the real bounded HTTP helper; no live model."""

import json
import traceback

import pytest
import requests
from astronverse.actionlib import managed_risk
from astronverse.ai.api import http, llm


@pytest.fixture(params=[False, True], ids=["ordinary", "managed"])
def managed(request, monkeypatch, tmp_path):
    for name, value in (("_contract", None), ("_audit", None), ("_count", 0), ("_violation", None)):
        monkeypatch.setattr(managed_risk, name, value)
    if request.param:
        contract = tmp_path / "request.risk.json"
        contract.write_text(
            json.dumps(
                {
                    "version": 1,
                    "approval": {"id": "synthetic-review"},
                    "operations": {"ChatAI.single_turn_chat": {"risk": "high"}},
                    "maxOperations": 1,
                    "codeHashes": [],
                }
            ),
            encoding="utf-8",
        )
        managed_risk.configure(contract)
    assert managed_risk.active() is request.param
    return request.param


@pytest.fixture(params=["chat_normal", "chat_prompt"])
def caller(request):
    if request.param == "chat_normal":
        return lambda: llm.chat_normal("question", system_input="system", model="fixture-model")
    return lambda: llm.chat_prompt("fixture-prompt", {"text": "question"}, model="fixture-model")


class Response:
    status_code = 200
    closed = False
    chunks = [b"{}"]
    read_error = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def iter_content(self, size):
        if self.read_error:
            raise requests.ReadTimeout("synthetic-secret")
        yield from self.chunks


@pytest.mark.parametrize("failure", ["connection", "timeout", "stream", "http", "malformed", "large"])
def test_request_failure_contract(monkeypatch, managed, caller, failure, capsys):
    response = Response()
    if failure == "http":
        response.status_code = 503
    elif failure == "malformed":
        response.chunks = [b"synthetic-secret"]
    elif failure == "large":
        response.chunks = [b"x" * (http.MAX_RESPONSE_BYTES + 1)]
    response.read_error = failure == "stream"
    logs = []
    monkeypatch.setattr(llm.logger, "info", logs.append)

    def request(*args, **kwargs):
        if failure == "connection":
            raise requests.ConnectionError("synthetic-secret")
        if failure == "timeout":
            raise requests.ConnectTimeout("synthetic-secret")
        return response

    # Keep llm.request_json real: this catches exception-contract drift at the caller.
    monkeypatch.setattr(requests, "request", request)
    if managed:
        with pytest.raises(RuntimeError, match="^AI_REQUEST_FAILED$") as error:
            caller()
        assert "synthetic-secret" not in "".join(traceback.format_exception(error.value))
        assert logs == []
    else:
        assert caller() is None
        assert logs == ["AI request failed"]
    assert failure in {"connection", "timeout"} or response.closed
    captured = capsys.readouterr()
    assert "synthetic-secret" not in captured.out + captured.err


@pytest.mark.parametrize("shape", ["normal", "normal-wrapped", "prompt"])
def test_success_payload_and_result(monkeypatch, managed, shape):
    response = Response()
    choices = {"choices": [{"message": {"content": "answer"}}]}
    payload = choices if shape == "normal" else {"data": choices}
    if shape == "prompt":
        payload = {"data": {"answer": "ok"}}
    response.chunks = [json.dumps(payload).encode()]
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs["json"]))
        return response

    monkeypatch.setattr(requests, "request", request)
    if shape == "prompt":
        assert llm.chat_prompt("fixture", {"text": "question"}, model="fixture-model") == {"answer": "ok"}
        expected_url = llm.PROMPT_URL
        expected_data = {"model": "fixture-model", "prompt_type": "fixture", "params": {"text": "question"}}
    else:
        assert llm.chat_normal("question", "system", model="fixture-model") == "answer"
        expected_url = llm.API_URL
        expected_data = {
            "model": "fixture-model",
            "messages": [{"role": "system", "content": "system"}, {"role": "user", "content": "question"}],
            "stream": False,
        }
    assert calls == [("POST", expected_url, expected_data)]
    assert response.closed


def test_unrelated_runtime_error_is_not_swallowed(monkeypatch, managed, caller):
    def request(*args, **kwargs):
        raise RuntimeError("unrelated failure")

    monkeypatch.setattr(requests, "request", request)
    with pytest.raises(RuntimeError, match="^unrelated failure$"):
        caller()
