import json

import pytest
import requests
from astronverse.ai.api import http
from astronverse.ai.api.dify import Dify
from astronverse.ai.api.xcagent import xcAgent


class Response:
    status_code = 200
    closed = False
    chunks = [b'{"answer":"ok"}']

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def iter_content(self, size):
        yield from self.chunks


def test_bounded_response_closed_and_no_redirect(monkeypatch):
    response = Response()
    calls = []
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: (calls.append(kwargs), response)[1])
    assert http.request_json("POST", "https://provider.invalid", json={"query": "fixture"}) == {"answer": "ok"}
    assert response.closed
    assert calls[0]["timeout"] == (5, 35)
    assert calls[0]["allow_redirects"] is False


@pytest.mark.parametrize("kind", ["redirect", "large", "malformed", "network"])
def test_failures_are_bounded_redacted_and_closed(monkeypatch, kind):
    response = Response()
    if kind == "redirect":
        response.status_code = 302
    elif kind == "large":
        response.chunks = [b"x" * (http.MAX_RESPONSE_BYTES + 1)]
    elif kind == "malformed":
        response.chunks = [b"secret-provider-error"]

    def request(*args, **kwargs):
        if kind == "network":
            raise requests.ConnectionError("secret-provider-error")
        return response

    monkeypatch.setattr(requests, "request", request)
    with pytest.raises(http.AIRequestError, match="^AI_REQUEST_FAILED$") as error:
        http.request_json("POST", "https://provider.invalid")
    assert isinstance(error.value, RuntimeError)
    assert kind == "network" or response.closed


def test_dify_failure_does_not_return_success_payload(monkeypatch):
    monkeypatch.setattr(
        "astronverse.ai.api.dify.request_json", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("secret"))
    )
    with pytest.raises(RuntimeError, match="^AI_REQUEST_FAILED$"):
        Dify("secret-token", "https://provider.invalid").run_workflow("fixture", "", False, "", "")


def test_astron_agent_input_mapping_and_cleanup(monkeypatch):
    class Connection:
        closed = False
        status = 200

        def request(self, method, path, body, headers):
            self.body = json.loads(body)

        def getresponse(self):
            return self

        def read(self, limit):
            return b'{"choices":[{"message":{"content":"ok"}}]}'

        def close(self):
            self.closed = True

    connection = Connection()
    monkeypatch.setattr("http.client.HTTPSConnection", lambda *a, **k: connection)
    assert (
        xcAgent("key", "secret").run_astron_flow(
            "flow", False, [{"key": "question", "value": "fixture", "type": "string"}]
        )
        == "ok"
    )
    assert connection.body["parameters"] == {"question": "fixture"}
    assert connection.closed


def test_astron_file_upload_uses_bounded_request_and_closes_file(monkeypatch, tmp_path):
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("synthetic", encoding="utf-8")
    streams = []

    def request(method, url, **kwargs):
        stream = kwargs["files"]["file"][1]
        assert stream.read() == b"synthetic"
        streams.append(stream)
        return {"data": {"url": "https://provider.invalid/fixture"}}

    monkeypatch.setattr("astronverse.ai.api.xcagent.request_json", request)
    agent = xcAgent("key", "secret")
    monkeypatch.setattr(agent, "_run", lambda flow, parameters, stream: parameters)
    assert agent.run_astron_flow("flow", False, [{"key": "file", "value": fixture, "type": "file"}]) == {
        "file": "https://provider.invalid/fixture"
    }
    assert streams[0].closed
