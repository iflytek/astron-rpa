import json
import os
import sys
import threading
import time
from typing import Any, Dict

from astronverse.browser_bridge import BROWSER_REGISTER_NAME

DEFAULT_NATIVE_TIMEOUT = 60
MAX_RESPONSE_LEN = 2 * 1024 * 1024  # 2MB
DEFAULT_CONNECT_TIMEOUT = 5.0  # 等待管道就绪的最长时间（秒）


class NativeMessagingClient:

    @staticmethod
    def _build_ipc_key(browser_type: str) -> str:
        exe_name = BROWSER_REGISTER_NAME.get(browser_type, "")
        if not exe_name:
            return ""
        base = os.path.basename(exe_name)
        name, _ = os.path.splitext(base)
        name = name.strip().replace(" ", "_").lower()
        if not name:
            return ""
        return f"ASTRON_{name.upper()}_PIPE"

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
                raise ConnectionError(
                    f"pipe exists but cannot connect: {pipe_name}: {e}"
                ) from e
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ConnectionError(
                    f"pipe not available after {connect_timeout}s: {pipe_name}"
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
        if not sys.platform.startswith("win"):
            raise RuntimeError("native messaging only supported on Windows")
        ipc_key = NativeMessagingClient._build_ipc_key(browser_type)
        if not ipc_key:
            raise ValueError(f"invalid browser_type for native messaging: {browser_type!r}")
        pipe_name = r"\\.\pipe\{}".format(ipc_key)
        payload = {"type": key, "data": data}
        message = json.dumps(payload, ensure_ascii=False) + "\n"
        result: list = [None]
        exc: list = [None]

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
