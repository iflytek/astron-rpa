import subprocess
import sys

import pyperclip


class ClipBoardCore:
    """剪贴板核心实现 - 补充 scheduler clipboard 缺失的方法"""

    @staticmethod
    def copy_str_clip(data: str = ""):
        """复制文本到剪贴板"""
        return pyperclip.copy(data)

    @staticmethod
    def clear_clip():
        """清空剪贴板"""
        return pyperclip.copy("")

    @staticmethod
    def copy_file_clip(file_path: str = ""):
        """复制文件到剪贴板"""
        if sys.platform == "win32":
            pyperclip.copy(file_path)
            subprocess.run(
                ["powershell", "-command", f'set-Clipboard -Path "{file_path}"'],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif sys.platform == "darwin":
            applescript = f'set the clipboard to (POSIX file "{file_path}")'
            subprocess.run(
                ["osascript", "-e", applescript],
                check=True,
                capture_output=True
            )
        else:  # Linux
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=file_path.encode(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    @staticmethod
    def paste_file_clip() -> str:
        """从剪贴板获取文件路径"""
        if sys.platform == "win32":
            import win32clipboard as cp
            from astronverse.system.error import BizException, CONTENT_TYPE_ERROR

            cp.OpenClipboard()
            try:
                file_list = cp.GetClipboardData(cp.CF_HDROP)
            except TypeError:
                cp.CloseClipboard()
                raise BizException(
                    CONTENT_TYPE_ERROR,
                    "剪切板中内容为文本内容，请检查剪切板内容及获取类型设置是否正确",
                )
            file_path = file_list[0]
            cp.CloseClipboard()
            return file_path
        elif sys.platform == "darwin":
            from astronverse.system.error import BizException, CONTENT_TYPE_ERROR

            applescript = '''
            try
                return POSIX path of (the clipboard as «class furl»)
            on error
                return ""
            end try
            '''
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            file_path = result.stdout.strip()
            if not file_path:
                raise BizException(
                    CONTENT_TYPE_ERROR,
                    "剪切板中内容为文本内容，请检查剪切板内容及获取类型设置是否正确"
                )
            return file_path
        else:  # Linux
            result = subprocess.run(
                ["xclip", "-o", "-selection", "clipboard"],
                check=True,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout.strip()
