import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import Mock

import pytest
from astronverse.network.core_ftp import FtpCore
from astronverse.network.core_network import NetworkCore
from astronverse.network.ftp import FTP


def test_get_and_head_return_json_serializable_data_from_http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 -- HTTP handler API
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"answer":42}')

        def do_HEAD(self):  # noqa: N802 -- HTTP handler API
            self.send_response(200)
            self.send_header("X-Answer", "42")
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/"
        assert json.loads(NetworkCore.get_request(url, timeout=2)) == {"answer": 42}
        headers = NetworkCore.head_request(url, timeout=2)
        assert type(headers) is dict
        assert json.loads(json.dumps(headers))["X-Answer"] == "42"
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
    assert not worker.is_alive()


def test_ftp_connection_has_finite_timeout():
    client = FtpCore.create_ftp()
    assert client.timeout == 30
    client.close()


@pytest.mark.parametrize("failure", ["connect", "login"])
def test_failed_ftp_connection_releases_socket_and_hides_password(monkeypatch, failure):
    client = Mock()
    getattr(client, failure).side_effect = RuntimeError("synthetic-secret")
    monkeypatch.setattr(FtpCore, "create_ftp", lambda: client)
    create = getattr(FTP.ftp_create, "__wrapped__", FTP.ftp_create)
    with pytest.raises(Exception) as error:
        create("127.0.0.1", 2121, "user", "synthetic-secret")
    assert "synthetic-secret" not in str(error.value)
    client.close.assert_called_once()
