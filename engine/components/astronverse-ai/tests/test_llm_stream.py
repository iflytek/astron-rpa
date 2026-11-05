import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from astronverse.ai.api import llm


def test_stream_skips_non_content_events_with_real_sse(monkeypatch):
    chunks = [
        {"choices": [{"delta": {"role": "assistant"}}]},
        {"choices": [{"delta": {"reasoning_content": "internal"}}]},
        {"choices": [{"delta": {"content": None}}]},
        {"choices": [{"delta": {"content": ""}}]},
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " world"}}]},
        {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        {"choices": [{"delta": None}]},
        {"choices": [{}]},
        {"choices": [], "usage": {"total_tokens": 10}},
    ]
    body = "".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks)
    body += "data: [DONE]\n\n"

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert request["stream"] is True
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    monkeypatch.setattr(llm, "API_URL", f"http://127.0.0.1:{server.server_port}/chat")
    try:
        assert list(llm.chat_streamable([{"role": "user", "content": "test"}])) == ["Hello", " world"]
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
    assert not worker.is_alive()


@pytest.mark.parametrize("payload", [b"data: invalid-json\n\n", b'data: {"choices":[]}\n\n'])
def test_response_is_closed_on_error_or_empty_stream(monkeypatch, payload):
    class Response:
        status_code = 200
        closed = False

        def __iter__(self):
            yield payload

        def close(self):
            self.closed = True

    response = Response()
    monkeypatch.setattr(llm.requests, "post", lambda *args, **kwargs: response)
    if b"invalid-json" in payload:
        with pytest.raises(json.JSONDecodeError):
            list(llm.chat_streamable([]))
    else:
        assert list(llm.chat_streamable([])) == []
    assert response.closed
