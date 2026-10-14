import hashlib
import io
import json
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest
from astronverse.scheduler.core.executor import managed_files
from astronverse.scheduler.core.executor.managed_files import FileTransferError, FileWorkspace


def bundle(data=b"source"):
    def item(name):
        identifier = str(uuid4())
        return {
            "fileId": identifier,
            "fileName": name,
            "url": "https://rpa.example/api/rpa-openapi/files/transfer/" + identifier,
            "token": "test-token-with-sufficient-length",
        }

    source = item("输入.txt")
    source.update(size=len(data), sha256=hashlib.sha256(data).hexdigest())
    return {
        "version": 1,
        "limits": {"maxFileBytes": managed_files.MAX_BYTES, "maxFiles": 8},
        "inputs": {"source": source},
        "outputs": {"target": item("结果.txt")},
        "office": [],
    }


class Response:
    def __init__(self, content, status=200):
        self.content, self.status_code = content, status
        self.raw = io.BytesIO(content)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def iter_bytes(self, *_):
        yield self.content


def test_private_workspace_roundtrip_and_restart_finalization(tmp_path, monkeypatch):
    declaration = bundle()
    requests = []

    def request(method, url, **kwargs):
        assert kwargs["follow_redirects"] is False
        assert kwargs["trust_env"] is False
        assert kwargs["verify"].check_hostname is True
        assert kwargs["timeout"].connect == 5
        assert kwargs["timeout"].read == 30
        requests.append((method, url))
        if method == "GET":
            return Response(b"source")
        data = kwargs["content"]
        metadata = {key: declaration["outputs"]["target"][key] for key in ["fileId", "fileName"]}
        metadata.update(size=len(data), sha256=hashlib.sha256(data).hexdigest(), expiresAt=1000)
        return Response(json.dumps(metadata).encode())

    monkeypatch.setattr(managed_files.httpx, "stream", request)
    workspace = FileWorkspace(tmp_path / "execution.files", "https://rpa.example", declaration)
    params = workspace.prepare(
        {"source": declaration["inputs"]["source"]["fileId"], "target": "output:target", "zero": 0}
    )
    assert Path(params["source"]).read_bytes() == b"source"
    assert params["zero"] == 0
    Path(params["target"]).write_bytes(b"converted")
    restored = FileWorkspace(workspace.directory, "https://rpa.example")
    result = restored.finish({"source": params["source"], "target": params["target"], "zero": 0, "value": False})
    assert result["data"] == {"zero": 0, "value": False}
    assert result["files"]["target"]["sha256"] == hashlib.sha256(b"converted").hexdigest()
    assert len(requests) == 2
    restored.cleanup()
    assert not workspace.directory.exists()


@pytest.mark.parametrize(
    "url",
    [
        "http://rpa.example/files/transfer/{id}",
        "https://evil.example/files/transfer/{id}",
        "https://rpa.example/files/transfer/{id}?key=x",
        "https://secret@rpa.example/files/transfer/{id}",
    ],
)
def test_transfer_origin_and_url_secrets_are_rejected(tmp_path, url):
    declaration = bundle()
    declaration["inputs"]["source"]["url"] = url.format(id=declaration["inputs"]["source"]["fileId"])
    with pytest.raises(FileTransferError):
        FileWorkspace(tmp_path / "execution.files", "https://rpa.example", declaration)


@pytest.mark.parametrize(("content", "status"), [(b"corrupted", 200), (b"source", 302), (b"source-too-long", 200)])
def test_failed_input_transfer_cleans_workspace(tmp_path, monkeypatch, content, status):
    declaration = bundle()
    monkeypatch.setattr(managed_files.httpx, "stream", lambda *args, **kwargs: Response(content, status))
    workspace = FileWorkspace(tmp_path / "execution.files", "https://rpa.example", declaration)
    with pytest.raises(FileTransferError):
        workspace.prepare({"source": declaration["inputs"]["source"]["fileId"], "target": "output:target"})
    assert not workspace.directory.exists()


def test_missing_office_fails_before_download_or_launch(tmp_path, monkeypatch):
    declaration = bundle()
    declaration["office"] = ["excel"]
    monkeypatch.setattr(managed_files, "office_available", lambda _: False)
    request = Mock()
    monkeypatch.setattr(managed_files.httpx, "stream", request)
    workspace = FileWorkspace(tmp_path / "execution.files", "https://rpa.example", declaration)
    with pytest.raises(FileTransferError, match="OFFICE_UNAVAILABLE"):
        workspace.prepare({})
    request.assert_not_called()


def test_outputs_cannot_escape_or_expose_local_workspace(tmp_path, monkeypatch):
    declaration = bundle()
    declaration["inputs"] = {}
    workspace = FileWorkspace(tmp_path / "execution.files", "https://rpa.example", declaration)
    params = workspace.prepare({"target": "output:target"})
    with pytest.raises(FileTransferError, match="FILE_OUTPUT_INVALID"):
        workspace.finish({"path": params["target"]})
    with pytest.raises(FileTransferError, match="FILE_OUTPUT_INVALID"):
        workspace.finish({"path": Path(params["target"]).as_posix()})
    outside = tmp_path / "private.txt"
    outside.write_bytes(b"private")
    try:
        Path(params["target"]).symlink_to(outside)
    except OSError:
        pytest.skip("Windows symlink privilege unavailable")
    with pytest.raises(FileTransferError, match="FILE_OUTPUT_INVALID"):
        workspace.finish({})
    workspace.cleanup()
    assert outside.read_bytes() == b"private"


def test_cleanup_does_not_require_a_valid_manifest(tmp_path):
    directory = tmp_path / "execution.files"
    directory.mkdir()
    (directory / "transfer.json").write_text("incomplete")
    FileWorkspace.cleanup_directory(directory)
    assert not directory.exists()
    outside = tmp_path / "unrelated"
    outside.mkdir()
    with pytest.raises(FileTransferError):
        FileWorkspace.cleanup_directory(outside)
    assert outside.exists()


@pytest.mark.parametrize("reused", [False, True])
def test_cleanup_targets_only_recorded_office_process_identity(tmp_path, monkeypatch, reused):
    import psutil

    directory = tmp_path / "execution.files"
    directory.mkdir()
    (directory / "office-123.json").write_text(json.dumps({"pid": 123, "created": 1.0}))
    process = Mock()
    process.create_time.return_value = 2.0 if reused else 1.0
    process.name.return_value = "wps.exe"
    monkeypatch.setattr(psutil, "Process", lambda pid: process if pid == 123 else None)
    FileWorkspace.cleanup_directory(directory)
    if reused:
        process.terminate.assert_not_called()
    else:
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=5)
    assert not directory.exists()
