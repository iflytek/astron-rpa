import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from astronverse.scheduler.core.terminal import terminal


class _FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, *args):
        self.messages.append(message.format(*args))

    def error(self, message, *args):
        self.messages.append(message.format(*args))

    def exception(self, message, *args):
        self.messages.append(message.format(*args))


class _FakeResponse:
    status_code = 200
    text = json.dumps({"data": "registered"})


class TerminalLoggingTest(unittest.TestCase):
    def test_password_generation_uses_secrets_module(self):
        with patch.object(terminal.secrets, "choice", return_value="A") as choice:
            assert terminal.generate_password(4) == "AAAA"

        assert choice.call_count == 4

    def test_registration_sends_password_without_logging_it(self):
        fake_logger = _FakeLogger()
        sent_requests = []

        def fake_post(**kwargs):
            sent_requests.append(kwargs)
            return _FakeResponse()

        service = SimpleNamespace(
            rpa_route_port=13159,
            terminal_mod=False,
            executor_mg=SimpleNamespace(status=lambda: False),
        )

        with (
            patch.object(terminal, "logger", fake_logger),
            patch.object(terminal, "terminal_id", "terminal-1"),
            patch.object(terminal, "terminal_pwd", "terminal-secret"),
            patch.object(terminal, "ips", ["127.0.0.1"]),
            patch.object(terminal.requests, "post", side_effect=fake_post),
            patch.object(terminal.Terminal, "get_device_name", return_value="test-host"),
            patch.object(terminal.Terminal, "get_account", return_value="tester"),
            patch.object(terminal.Terminal, "get_os_info", return_value="Windows"),
            patch.object(terminal.Terminal, "get_cpu_percent", return_value=1),
            patch.object(terminal.Terminal, "get_memory_percent", return_value=2),
            patch.object(terminal.Terminal, "get_disk_percent", return_value=3),
        ):
            result = terminal.Terminal.register(service)

        assert result == "registered"
        assert sent_requests[0]["json"]["osPwd"] == "terminal-secret"
        assert "terminal-secret" not in "\n".join(fake_logger.messages)


if __name__ == "__main__":
    unittest.main()
