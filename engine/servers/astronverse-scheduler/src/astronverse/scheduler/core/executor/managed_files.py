"""Origin-bound transfers for a managed execution's private file workspace."""

import hashlib
import json
import os
import re
import shutil
import ssl
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

import httpx

MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 8


class FileTransferError(ValueError):
    def __init__(self, code="FILE_TRANSFER_FAILED"):
        super().__init__(code)
        self.code = code


def safe_name(value):
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= 160
        or value in {".", ".."}
        or value[-1:] in {".", " "}
        or re.search(r'[\\/:<>"|?*\x00-\x1f\x7f]', value)
        or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", value, re.IGNORECASE)
    ):
        raise FileTransferError("FILE_OUTPUT_INVALID")
    return value


def office_available(application):
    if os.name != "nt":
        return False
    import winreg

    keys = {
        "excel": ("Excel.Application", "Ket.Application", "et.Application"),
        "word": ("Word.Application", "Kwps.Application", "wps.Application"),
    }
    for name in keys.get(application, ()):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, name + "\\CLSID"):
                return True
        except OSError:
            pass
    return False


class FileWorkspace:
    def __init__(self, directory, origin, bundle=None):
        self.directory = Path(directory).absolute()
        if self.directory.is_symlink() or self.directory.resolve() != self.directory:
            raise FileTransferError("FILE_OUTPUT_INVALID")
        self.origin = urlsplit(origin)
        self.manifest = self.directory / "transfer.json"
        if bundle is None:
            bundle = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.bundle = bundle
        if (
            not isinstance(bundle, dict)
            or bundle.get("version") != 1
            or bundle.get("limits", {}).get("maxFileBytes") != MAX_BYTES
            or bundle.get("limits", {}).get("maxFiles") != MAX_FILES
            or not isinstance(bundle.get("inputs"), dict)
            or not isinstance(bundle.get("outputs"), dict)
            or not 1 <= len(bundle["inputs"]) + len(bundle["outputs"]) <= MAX_FILES
            or set(bundle["inputs"]) & set(bundle["outputs"])
        ):
            raise FileTransferError()
        for side in ("inputs", "outputs"):
            for key, item in bundle[side].items():
                if not isinstance(key, str) or not key.isidentifier() or not isinstance(item, dict):
                    raise FileTransferError()
                safe_name(item.get("fileName"))
                self.url(item)

    def url(self, item):
        parsed = urlsplit(item.get("url", ""))
        try:
            identifier = str(UUID(item.get("fileId")))
        except (ValueError, TypeError, AttributeError):
            raise FileTransferError() from None
        if (
            parsed.scheme != "https"
            or self.origin.scheme != "https"
            or (parsed.hostname, parsed.port or 443) != (self.origin.hostname, self.origin.port or 443)
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or not parsed.path.endswith("/files/transfer/" + identifier)
            or not isinstance(item.get("token"), str)
            or not 20 <= len(item["token"]) <= 100
        ):
            raise FileTransferError()
        return item["url"]

    def path(self, side, key, item):
        folder = hashlib.sha256(key.encode()).hexdigest()[:20]
        path = self.directory / side / folder / safe_name(item["fileName"])
        if not path.resolve().is_relative_to(self.directory) or any(p.is_symlink() for p in [path, *path.parents]):
            raise FileTransferError("FILE_OUTPUT_INVALID")
        return path

    def request(self, method, item, data=None):
        # Match RemoteTransport's verified Windows/system trust and explicit
        # no-proxy/no-redirect policy; do not inherit ambient proxy credentials.
        return httpx.stream(
            method,
            self.url(item),
            headers={"Authorization": "Bearer " + item["token"], "Content-Type": "application/octet-stream"},
            content=data,
            follow_redirects=False,
            verify=ssl.create_default_context(),
            trust_env=False,
            timeout=httpx.Timeout(30, connect=5),
        )

    def prepare(self, params):
        for application in self.bundle.get("office", []):
            if not office_available(application):
                raise FileTransferError("OFFICE_UNAVAILABLE")
        self.directory.mkdir(parents=True, exist_ok=False, mode=0o700)
        self.manifest.write_text(json.dumps(self.bundle), encoding="utf-8")
        self.manifest.chmod(0o600)
        result = dict(params)
        try:
            for key, item in self.bundle["inputs"].items():
                if params.get(key) != item["fileId"] or not 0 <= item.get("size", -1) <= MAX_BYTES:
                    raise FileTransferError()
                path = self.path("inputs", key, item)
                path.parent.mkdir(parents=True, mode=0o700)
                digest = hashlib.sha256()
                size = 0
                with self.request("GET", item) as response, path.open("xb") as stream:
                    if response.status_code != 200:
                        raise FileTransferError()
                    for chunk in response.iter_bytes(65536):
                        size += len(chunk)
                        if size > item["size"] or size > MAX_BYTES:
                            raise FileTransferError()
                        stream.write(chunk)
                        digest.update(chunk)
                if size != item["size"] or digest.hexdigest() != item["sha256"]:
                    raise FileTransferError()
                result[key] = str(path)
            for key, item in self.bundle["outputs"].items():
                if params.get(key) != "output:" + key:
                    raise FileTransferError()
                path = self.path("outputs", key, item)
                path.parent.mkdir(parents=True, mode=0o700)
                result[key] = str(path)
        except (OSError, httpx.HTTPError, ValueError, KeyError, TypeError):
            self.cleanup()
            raise FileTransferError() from None
        return result

    def finish(self, value):
        # The executor echoes input parameters at the result root. Remove only
        # exact echoes of declared file bindings; other local path disclosures
        # still fail validation below.
        if isinstance(value, dict):
            value = dict(value)
            for side in ("inputs", "outputs"):
                for key, item in self.bundle[side].items():
                    if value.get(key) == str(self.path(side, key, item)):
                        value.pop(key)
        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
        # Local workspace paths are never public result values; return handles instead.
        root = str(self.directory).replace("\\", "/").casefold()
        if root in serialized.replace("\\\\", "/").replace("\\", "/").casefold():
            raise FileTransferError("FILE_OUTPUT_INVALID")
        outputs = {}
        for key, item in self.bundle["outputs"].items():
            path = self.path("outputs", key, item)
            if not path.is_file() or path.stat().st_size > MAX_BYTES:
                raise FileTransferError("FILE_OUTPUT_INVALID")
            with path.open("rb") as stream:
                data = stream.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise FileTransferError("FILE_OUTPUT_INVALID")
            with self.request("PUT", item, data) as response:
                if response.status_code != 200:
                    raise FileTransferError()
                payload = bytearray()
                for chunk in response.iter_bytes(4096):
                    if len(payload) + len(chunk) > 4096:
                        raise FileTransferError()
                    payload.extend(chunk)
                metadata = json.loads(payload)
            if (
                metadata.get("fileId") != item["fileId"]
                or metadata.get("fileName") != item["fileName"]
                or metadata.get("size") != len(data)
                or metadata.get("sha256") != hashlib.sha256(data).hexdigest()
            ):
                raise FileTransferError()
            outputs[key] = metadata
        return {"data": value, "files": outputs}

    def cleanup(self):
        self.cleanup_directory(self.directory)

    @staticmethod
    def cleanup_directory(directory):
        directory = Path(directory).absolute()
        if directory.exists():
            if directory.is_symlink() or directory.resolve() != directory or directory.suffix != ".files":
                raise FileTransferError("FILE_OUTPUT_INVALID")
            # Called only before launch or after the exact executor has stopped.
            # Never close all Office processes or rely on a reusable PID alone.
            import psutil

            for record in directory.glob("office-*.json"):
                if record.is_symlink():
                    raise FileTransferError("FILE_OUTPUT_INVALID")
                try:
                    value = json.loads(record.read_text(encoding="utf-8"))
                    process = psutil.Process(value["pid"])
                    if process.create_time() == value["created"]:
                        if process.name().lower() not in {"excel.exe", "winword.exe", "et.exe", "wps.exe"}:
                            raise FileTransferError("FILE_OUTPUT_INVALID")
                        process.terminate()
                        process.wait(timeout=5)
                except psutil.NoSuchProcess:
                    pass
                except (psutil.Error, KeyError, TypeError, ValueError):
                    raise FileTransferError("FILE_OUTPUT_INVALID") from None
            shutil.rmtree(directory)
