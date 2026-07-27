import pytest

from app.utils.url import join_api_url


@pytest.mark.parametrize(
    ("base_url", "path", "expected"),
    [
        (
            "https://api.atlascloud.ai/v1",
            "models",
            "https://api.atlascloud.ai/v1/models",
        ),
        (
            "https://api.atlascloud.ai/v1/",
            "/chat/completions",
            "https://api.atlascloud.ai/v1/chat/completions",
        ),
        (
            "http://localhost:11434/v1",
            "chat/completions",
            "http://localhost:11434/v1/chat/completions",
        ),
    ],
)
def test_join_api_url_preserves_base_path(
    base_url: str,
    path: str,
    expected: str,
) -> None:
    assert join_api_url(base_url, path) == expected
