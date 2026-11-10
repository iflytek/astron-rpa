import os
from pathlib import Path

import pytest
from astronverse.scheduler.apis.connector import tools
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    work_dir = tmp_path / "work"
    (work_dir / "logs" / "report" / "p1").mkdir(parents=True)
    (work_dir / "logs" / "report" / "p1" / "e1.txt").write_text("log line", encoding="utf-8")
    (work_dir / ".setting.json").write_text("{}", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("secret", encoding="utf-8")
    monkeypatch.chdir(work_dir)

    app = FastAPI()
    app.include_router(tools.router)
    with TestClient(app) as test_client:
        yield test_client


def test_read_setting_file(client):
    response = client.post("/file/read", json={"path": "./.setting.json"})
    assert response.status_code == 200
    assert response.text == "{}"


def test_read_log_file(client):
    response = client.post("/file/read", json={"path": os.path.join("logs", "report", "p1", "e1.txt")})
    assert response.status_code == 200
    assert response.text == "log line"


@pytest.mark.parametrize("path", ["../secret.txt", "logs/../../secret.txt", "C:/Windows/win.ini", "/etc/passwd"])
def test_read_outside_allowed_area_is_rejected(client, path):
    assert client.post("/file/read", json={"path": path}).status_code == 403


def test_read_logs_dir_itself_is_rejected(client):
    assert client.post("/file/read", json={"path": "logs"}).status_code == 403


def test_write_setting_file(client):
    response = client.post("/file/write", json={"path": "./.setting.json", "content": '{"a": 1}'})
    assert response.status_code == 200
    assert Path(".setting.json").read_text(encoding="utf-8") == '{"a": 1}'


@pytest.mark.parametrize("path", ["logs/report/p1/e1.txt", "../evil.py", "other.json", "C:/Users/Public/evil.bat"])
def test_write_outside_setting_file_is_rejected(client, path):
    assert client.post("/file/write", json={"path": path, "content": "x"}).status_code == 403
