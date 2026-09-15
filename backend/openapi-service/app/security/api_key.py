"""Common API-key credential parsing and hash verification for MCP and REST."""

from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qs

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import OpenAPIDB
from app.utils.api_key import APIKeyUtils


class APIKeyAuthenticationError(ValueError):
    """Raised when a request does not contain one unambiguous credential."""


def _get_header_values(scope: Mapping[str, Any], name: bytes) -> list[str]:
    values = []
    for raw_name, raw_value in scope.get("headers", []):
        if raw_name.lower() == name:
            values.append(raw_value.decode("latin-1").strip())
    return values


def extract_api_key(scope: Mapping[str, Any], *, allow_query_api_key: bool = False) -> str:
    """Extract exactly one API key from the supported credential locations."""
    credentials: list[str] = []

    authorization_values = _get_header_values(scope, b"authorization")
    if len(authorization_values) > 1:
        raise APIKeyAuthenticationError("Multiple Authorization headers are not allowed")
    if authorization_values:
        parts = authorization_values[0].split()
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
            raise APIKeyAuthenticationError("Invalid Authorization header")
        credentials.append(parts[1])

    api_key_header_values = _get_header_values(scope, b"x-api-key")
    if len(api_key_header_values) > 1 or (api_key_header_values and not api_key_header_values[0]):
        raise APIKeyAuthenticationError("Invalid X-API-Key header")
    if api_key_header_values:
        credentials.append(api_key_header_values[0])

    query_values = parse_qs(
        scope.get("query_string", b"").decode("latin-1"),
        keep_blank_values=True,
    ).get("key", [])
    if query_values:
        if not allow_query_api_key:
            raise APIKeyAuthenticationError("Query parameter API keys are disabled")
        if len(query_values) != 1 or not query_values[0].strip():
            raise APIKeyAuthenticationError("Invalid query parameter API key")
        credentials.append(query_values[0].strip())

    if len(credentials) != 1:
        raise APIKeyAuthenticationError("Exactly one API key credential is required")

    return credentials[0]


def has_api_key_credential(scope: Mapping[str, Any]) -> bool:
    return bool(
        _get_header_values(scope, b"authorization")
        or _get_header_values(scope, b"x-api-key")
        or "key" in parse_qs(scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True)
    )


async def validate_api_key(db: AsyncSession, raw_key: str) -> str | None:
    # bcrypt truncates after 72 bytes in some versions. Never authenticate a
    # different, longer credential by silently comparing only its prefix.
    if not raw_key or len(raw_key.encode("utf-8")) > 72:
        return None
    result = await db.execute(select(OpenAPIDB).where(OpenAPIDB.prefix == raw_key[:8], OpenAPIDB.is_active == 1))
    for key in result.scalars().all():
        try:
            valid = APIKeyUtils.verify_api_key(raw_key, key.api_key)
        except (ValueError, TypeError, AttributeError):
            # A corrupt stored hash must not authenticate or expose DB values.
            continue
        if valid and key.user_id:
            return str(key.user_id)
    return None
