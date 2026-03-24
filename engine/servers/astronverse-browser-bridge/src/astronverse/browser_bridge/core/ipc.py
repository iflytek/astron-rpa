import hashlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
from contextlib import closing
from typing import Any, Dict

from astronverse.browser_bridge import BROWSER_REGISTER_NAME
from astronverse.browser_bridge.error import BizException, INVALID_BROWSER_TYPE

DEFAULT_NATIVE_TIMEOUT = 60
MAX_RESPONSE_LEN = 2 * 1024 * 1024  # 2MB
DEFAULT_CONNECT_TIMEOUT = 5.0  # 等待管道/套接字就绪的最长时间（秒）
# 与 engine/binaries/native_messaging/internal/ipc_linux.go 中 maxUnixSockPath 一致
_MAX_UNIX_SOCK_PATH_LEN = 100


def browser_ipc_alias(browser_type: str) -> str:
    """返回用于推导 ipcKey 的规范名称（每组首项，与 Go astronPipe(al[0]) 一致）。"""
    entry = BROWSER_REGISTER_NAME.get(browser_type, [])
    return entry[0] if entry else ""


class NativeMessagingClient:
    @staticmethod
    def _build_ipc_key(browser_type: str) -> str:
        exe_name = browser_ipc_alias(browser_type)
        if not exe_name:
            return ""
        base = os.path.basename(exe_name)
        name, _ = os.path.splitext(base)
        name = name.strip().replace(" ", "_").lower()
        if not name:
            return ""
        return f"ASTRON_{name.upper()}_PIPE"

    @staticmethod
    def _sanitize_for_filename(s: str) -> str:
        out = []
        for ch in s:
            if ch.isalnum() or ch in ("_", "-"):
                out.append(ch)
        return "".join(out) if out else "ipc"

    @staticmethod
    def _unix_socket_dir() -> str:
        runtime_dir = (os.environ.get("XDG_RUNTIME_DIR") or "").strip()
        if runtime_dir:
            sub = os.path.join(runtime_dir, "astra-native-msg")
            try:
                os.makedirs(sub, mode=0o700, exist_ok=True)
                return sub
            except OSError:
                pass
        sub = os.path.join(tempfile.gettempdir(), "astra-native-msg")
        os.makedirs(sub, mode=0o700, exist_ok=True)
        return sub

    @staticmethod
    def _unix_socket_path(ipc_key: str) -> str:
        """与 native_messaging InitIPC（Linux/macOS）生成的 sock 路径一致。"""
        directory = NativeMessagingClient._unix_socket_dir()
        base = NativeMessagingClient._sanitize_for_filename(ipc_key) + ".sock"
        path = os.path.join(directory, base)
        if len(path) > _MAX_UNIX_SOCK_PATH_LEN:
            digest = hashlib.sha256(ipc_key.encode("utf-8")).digest()
            short = "astra-" + digest[:8].hex() + ".sock"
            path = os.path.join(directory, short)
            if len(path) > _MAX_UNIX_SOCK_PATH_LEN:
                raise OSError(
                    f"unix socket path too long after shortening: {len(path)} bytes"
                )
        return path

    @staticmethod
    def _readline_from_socket(sock: socket.socket) -> bytes:
        buf = b""
        while b"\n" not in buf and len(buf) < MAX_RESPONSE_LEN:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
        if not buf:
            return b""
        if b"\n" in buf:
            end = buf.index(b"\n") + 1
            return buf[:end]
        return buf

    @staticmethod
    def _open_pipe(pipe_name: str, connect_timeout: float = DEFAULT_CONNECT_TIMEOUT):
        deadline = time.monotonic() + connect_timeout
        interval = 0.05
        last_err = None
        while True:
            try:
                return open(pipe_name, "w+b", buffering=0)
            except FileNotFoundError as e:
                last_err = e
            except PermissionError as e:
                last_err = e
            except OSError as e:
                raise ConnectionError(f"pipe exists but cannot connect: {pipe_name}: {e}") from e
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ConnectionError(f"pipe not available after {connect_timeout}s: {pipe_name}") from last_err
            time.sleep(min(interval, remaining))
            interval = min(interval * 1.5, 1.0)

    @staticmethod
    def _open_unix_socket(
            sock_path: str, connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    ) -> socket.socket:
        deadline = time.monotonic() + connect_timeout
        interval = 0.05
        last_err = None
        while True:
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                try:
                    s.connect(sock_path)
                except OSError:
                    s.close()
                    raise
                return s
            except (FileNotFoundError, ConnectionError, OSError) as e:
                last_err = e
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ConnectionError(
                    f"unix socket not available after {connect_timeout}s: {sock_path}"
                ) from last_err
            time.sleep(min(interval, remaining))
            interval = min(interval * 1.5, 1.0)

    @staticmethod
    def send_and_wait(
            browser_type: str,
            key: str,
            data: Dict[str, Any],
            connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
            timeout: float = DEFAULT_NATIVE_TIMEOUT,
    ) -> Dict[str, Any]:
        ipc_key = NativeMessagingClient._build_ipc_key(browser_type)
        if not ipc_key:
            raise BizException(INVALID_BROWSER_TYPE.format(browser_type), f"无效的浏览器类型: {browser_type}")
        payload = {"type": key, "data": data}
        message = json.dumps(payload, ensure_ascii=False) + "\n"
        result: list = [None]
        exc: list = [None]

        if sys.platform == "win32":
            pipe_name = r"\\.\pipe\{}".format(ipc_key)

            def read_response(pipe_fd):
                try:
                    pipe_fd.write(message.encode("utf-8"))
                    pipe_fd.flush()
                    raw = pipe_fd.readline()
                    result[0] = raw if raw else b""
                except Exception as e:
                    exc[0] = e

            with NativeMessagingClient._open_pipe(pipe_name, connect_timeout) as pipe:
                th = threading.Thread(target=read_response, args=(pipe,))
                th.daemon = True
                th.start()
                th.join(timeout=timeout)
                if exc[0] is not None:
                    raise exc[0]
                if result[0] is None:
                    raise TimeoutError(
                        "timeout waiting for native messaging response ({}s)".format(timeout)
                    )
        else:
            sock_path = NativeMessagingClient._unix_socket_path(ipc_key)

            def read_response(sock: socket.socket):
                try:
                    sock.sendall(message.encode("utf-8"))
                    raw = NativeMessagingClient._readline_from_socket(sock)
                    result[0] = raw if raw else b""
                except Exception as e:
                    exc[0] = e

            with closing(
                    NativeMessagingClient._open_unix_socket(sock_path, connect_timeout)
            ) as sock:
                th = threading.Thread(target=read_response, args=(sock,))
                th.daemon = True
                th.start()
                th.join(timeout=timeout)
                if exc[0] is not None:
                    raise exc[0]
                if result[0] is None:
                    raise TimeoutError(
                        "timeout waiting for native messaging response ({}s)".format(timeout)
                    )

        raw = result[0]
        if not raw:
            return {}
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
