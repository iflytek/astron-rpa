import os
import sys


def get_cmd():
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(__file__), "win", "astron_router.exe")
    else:
        return os.path.join(os.path.dirname(__file__), "linux", "astron_router.exe")
