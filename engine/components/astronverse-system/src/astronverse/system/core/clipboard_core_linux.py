import subprocess

import pyperclip
from astronverse.system.core.clipboard_core import IClipBoardCore


class ClipBoardCore(IClipBoardCore):
    @staticmethod
    def copy_str_clip(data: str = ""):
        return pyperclip.copy(data)

    @staticmethod
    def paste_str_clip() -> str:
        return pyperclip.paste()

    @staticmethod
    def clear_clip():
        return pyperclip.copy("")

    @staticmethod
    def copy_file_clip(file_path: str = ""):
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=file_path.encode(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @staticmethod
    def paste_file_clip() -> str:
        try:
            result = subprocess.run(
                ["xclip", "-o", "-selection", "clipboard"],
                check=True,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise e

    @staticmethod
    def paste_html_clip() -> str:
        raise NotImplementedError()
