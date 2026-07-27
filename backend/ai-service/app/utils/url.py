from urllib.parse import urljoin


def join_api_url(base_url: str, path: str) -> str:
    """Join an API path without dropping a version prefix from the base URL."""
    normalized_base = f"{base_url.rstrip('/')}/"
    return urljoin(normalized_base, path.lstrip("/"))
