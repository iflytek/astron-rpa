import logging
import re

REDACTED = "[REDACTED]"

_SENSITIVE_KEY = (
    r"(?:api[ _-]?key|api[ _-]?secret|hashed[ _-]?key|password|passwd|pwd|"
    r"confirm[ _-]?password|old[ _-]?password|new[ _-]?password|"
    r"access[ _-]?token|refresh[ _-]?token|id[ _-]?token|temp[ _-]?token|token|"
    r"authorization|cookie|cache[ _-]?key|session(?:[ _-]?id)?|jsessionid|casdoor[ _-]?session[ _-]?id|"
    r"verification[ _-]?code|verify[ _-]?code|sms[ _-]?code|captcha|credential)"
)

_QUOTED_VALUE = re.compile(rf"(?i)([\"']{_SENSITIVE_KEY}[\"']\s*[:=]\s*[\"'])(.*?)([\"'])")
_QUOTED_ARRAY_VALUE = re.compile(rf"(?i)([\"']{_SENSITIVE_KEY}[\"']\s*[:=]\s*\[)[^\]]*(\])")
_LABEL_VALUE = re.compile(rf"(?i)(\b{_SENSITIVE_KEY}\b\s*[:=：]\s*)(?!{re.escape(REDACTED)})([^\s,;&}}\]]+)")
_CHINESE_SECRET_VALUE = re.compile(
    rf"((?:临时凭证|验证码|密码|口令|访问令牌|刷新令牌|会话(?:\s*ID)?|密钥)"
    rf"\s*[:=：]\s*)(?!{re.escape(REDACTED)})([^\s,，；}}\]]+)"
)
_BEARER_VALUE = re.compile(r"(?i)(\bBearer\s+)([^\s,;]+)")
_QUERY_API_KEY = re.compile(r"(?i)([?&]key=)([^&\s]+)")
_COOKIE_HEADER = re.compile(r"(?i)(\bCookie(?:\s+header)?\s*[:=]\s*)([^\r\n]+)")
_PHONE_VALUE = re.compile(r"(?i)((?:phone|mobile|手机号)\s*[\"']?\s*[:=：]\s*[\"']?)(1\d{2})\d{4}(\d{4})")
_BARE_PHONE_VALUE = re.compile(r"(?<!\d)(1\d{2})\d{4}(\d{4})(?!\d)")


def redact_sensitive_text(value: object) -> str:
    """Return a redacted log copy without mutating the source value."""
    if value is None:
        return ""

    text = str(value)
    text = _QUOTED_ARRAY_VALUE.sub(rf'\1"{REDACTED}"\2', text)
    text = _QUOTED_VALUE.sub(rf"\1{REDACTED}\3", text)
    text = _COOKIE_HEADER.sub(rf"\1{REDACTED}", text)
    text = _BEARER_VALUE.sub(rf"\1{REDACTED}", text)
    text = _QUERY_API_KEY.sub(rf"\1{REDACTED}", text)
    text = _LABEL_VALUE.sub(rf"\1{REDACTED}", text)
    text = _CHINESE_SECRET_VALUE.sub(rf"\1{REDACTED}", text)
    text = _PHONE_VALUE.sub(r"\1\2****\3", text)
    return _BARE_PHONE_VALUE.sub(r"\1****\2", text)


class SensitiveDataFilter(logging.Filter):
    """Redact the rendered message while leaving application objects unchanged."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if record.exc_info:
                # All standard formatters reuse exc_text when it is present.
                # Populate a sanitized copy so external handlers cannot emit the raw error.
                formatter = logging.Formatter()
                record.exc_text = redact_sensitive_text(formatter.formatException(record.exc_info))

            if record.name == "uvicorn.access" and isinstance(record.args, tuple):
                # AccessFormatter unpacks its five arguments while rendering.
                # Preserve that contract and sanitize only the copied strings.
                record.args = tuple(
                    redact_sensitive_text(item) if isinstance(item, str) else item for item in record.args
                )
                return True

            record.msg = redact_sensitive_text(record.getMessage())
            record.args = ()
        except Exception:
            # Logging must never break the application request path.
            record.msg = "[log message unavailable]"
            record.args = ()
        return True


class SensitiveFormatter(logging.Formatter):
    """Also redact exception text emitted by application handlers."""

    def formatException(self, exc_info) -> str:  # noqa: N802
        return redact_sensitive_text(super().formatException(exc_info))
