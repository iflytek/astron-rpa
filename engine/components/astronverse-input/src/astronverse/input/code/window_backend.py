import sys
from typing import Any


def window_find(pick: Any) -> Any:
    backend = _load_backend()
    return backend.window_find(pick)


def window_info(handler: Any) -> Any:
    backend = _load_backend()
    return backend.window_info(handler)


def window_top(handler: Any) -> None:
    backend = _load_backend()
    return backend.window_top(handler)


def _load_backend():
    if sys.platform == "win32":
        from astronverse.input.code import win32gui as backend

        return backend

    from astronverse.input.code import window_backend_stub as backend

    return backend
