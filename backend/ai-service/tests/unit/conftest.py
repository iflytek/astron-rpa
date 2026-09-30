"""Offline tests: run with pytest --confcutdir=tests/unit tests/unit."""

import pytest


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch, tmp_path):
    values = {
        "DATABASE_URL": "mysql+aiomysql://unit:unit@127.0.0.1:1/unit",
        "DATABASE_USERNAME": "unit",
        "DATABASE_PASSWORD": "unit",
        "REDIS_URL": "redis://127.0.0.1:1/0",
        "AICHAT_BASE_URL": "https://chat.invalid/v1/",
        "AICHAT_API_KEY": "unit",
        "CUA_BASE_URL": "https://cua.invalid/v1/",
        "CUA_API_KEY": "unit",
        "XFYUN_APP_ID": "unit",
        "XFYUN_API_SECRET": "unit",
        "XFYUN_API_KEY": "unit",
        "JFBYM_API_TOKEN": "unit",
        "LOG_DIR": str(tmp_path),
        "JEV_API_KEY": "",
        "JEV_MODEL": "jev-latest",
        "JEV_TIMEOUT_SECONDS": "10",
        "JEV_POINTS_COST": "100",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
