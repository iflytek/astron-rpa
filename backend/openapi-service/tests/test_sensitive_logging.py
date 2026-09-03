import logging
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from uvicorn.logging import AccessFormatter

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/test")
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.schemas.api_key import ApiKeyCreate
from app.services.api_key import ApiKeyService
from app.services.websocket import ws_log
from app.utils.api_key import APIKeyUtils
from app.utils.sensitive_logging import SensitiveDataFilter, SensitiveFormatter, redact_sensitive_text


@pytest.mark.parametrize(
    ("source", "secrets", "expected"),
    [
        (
            '{"password":"secret password","access_token":"token-123","status":200}',
            ("secret password", "token-123"),
            '"status":200',
        ),
        (
            '{"password":["first-secret","second-secret"],"status":200}',
            ("first-secret", "second-secret"),
            '"password":["[REDACTED]"]',
        ),
        (
            "Authorization: Bearer bearer-secret",
            ("bearer-secret",),
            "Authorization: [REDACTED]",
        ),
        (
            "/mcp?key=query-secret&mode=list",
            ("query-secret",),
            "?key=[REDACTED]&mode=list",
        ),
        (
            "phone: 13800138000",
            ("13800138000",),
            "phone: 138****8000",
        ),
        (
            "keyword: 13800138000, 密码：chinese-secret",
            ("13800138000", "chinese-secret"),
            "keyword: 138****8000",
        ),
        (
            "cacheKey: auth:temp_token:temporary-secret",
            ("temporary-secret",),
            "cacheKey: [REDACTED]",
        ),
    ],
)
def test_redact_sensitive_text(source, secrets, expected):
    sanitized = redact_sensitive_text(source)

    assert expected in sanitized
    for secret in secrets:
        assert secret not in sanitized


def test_sensitive_filter_redacts_rendered_message_without_mutating_source():
    payload = {"password": "secret", "phone": "13800138000", "status": "ok"}
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="payload=%s",
        args=(payload,),
        exc_info=None,
    )

    assert SensitiveDataFilter().filter(record) is True
    rendered = record.getMessage()

    assert "secret" not in rendered
    assert "13800138000" not in rendered
    assert payload == {"password": "secret", "phone": "13800138000", "status": "ok"}


def test_sensitive_formatter_redacts_exception_text():
    try:
        raise RuntimeError("access_token=exception-secret")
    except RuntimeError:
        exception_text = SensitiveFormatter().formatException(sys.exc_info())

    assert "exception-secret" not in exception_text
    assert "access_token=[REDACTED]" in exception_text


def test_sensitive_filter_preserves_uvicorn_access_formatter_contract():
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:12345", "GET", "/mcp?key=access-secret", "1.1", 200),
        exc_info=None,
    )

    assert SensitiveDataFilter().filter(record) is True
    rendered = AccessFormatter("%(message)s").format(record)

    assert "access-secret" not in rendered
    assert "/mcp?key=[REDACTED]" in rendered
    assert record.args[-1] == 200


def test_sensitive_filter_redacts_exception_for_external_formatter():
    try:
        raise RuntimeError("session_id=exception-session-secret")
    except RuntimeError:
        record = logging.LogRecord(
            name="uvicorn.error",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Request failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    assert SensitiveDataFilter().filter(record) is True
    rendered = logging.Formatter("%(message)s").format(record)

    assert "exception-session-secret" not in rendered
    assert "session_id=[REDACTED]" in rendered


@pytest.mark.parametrize(
    "message",
    [
        ('>>>{"custom_input":"outbound-secret"}',),
        ('<<<{"custom_output":"inbound-secret"}',),
        ('error ExitMsg: {"custom_input":"error-secret"}',),
    ],
)
def test_websocket_log_callback_does_not_log_message_payload(monkeypatch, message):
    log_methods = (MagicMock(), MagicMock(), MagicMock())
    monkeypatch.setattr("app.services.websocket.logger.debug", log_methods[0])
    monkeypatch.setattr("app.services.websocket.logger.info", log_methods[1])
    monkeypatch.setattr("app.services.websocket.logger.warning", log_methods[2])

    ws_log(message)

    calls = [call for method in log_methods for call in method.call_args_list]
    assert len(calls) == 1
    assert all("secret" not in str(call) for call in calls)


@pytest.mark.asyncio
async def test_api_key_creation_returns_key_without_logging_it(monkeypatch):
    raw_key = "raw-generated-api-key"
    db = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    service = ApiKeyService(db)
    service._invalidate_api_keys_cache = AsyncMock()
    log_info = MagicMock()

    monkeypatch.setattr(APIKeyUtils, "generate_api_key", MagicMock(return_value=raw_key))
    monkeypatch.setattr(APIKeyUtils, "hash_api_key", MagicMock(return_value="stored-hash"))
    monkeypatch.setattr("app.services.api_key.logger.info", log_info)

    result = await service.create_api_key(ApiKeyCreate(name="test-key"), "user-1")

    assert result == raw_key
    assert all(raw_key not in str(call) for call in log_info.call_args_list)


def test_api_key_verification_does_not_change_behavior():
    raw_key = "verification-key"
    hashed_key = APIKeyUtils.hash_api_key(raw_key)

    assert APIKeyUtils.verify_api_key(raw_key, hashed_key) is True
    assert APIKeyUtils.verify_api_key("wrong-key", hashed_key) is False
