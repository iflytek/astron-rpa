import re
import subprocess
import sys
from enum import Enum

import pyperclip


class Base64CodeType(Enum):
    STRING = "string"
    PICTURE = "picture"


class Clipboard:
    @staticmethod
    def paste_str_clip() -> str:
        """
        获取剪切板
        :return:
        """
        return pyperclip.paste()

    @staticmethod
    def paste_html_clip() -> str:
        if sys.platform == "win32":
            return Clipboard._paste_html_clip_win32()
        elif sys.platform == "darwin":
            return Clipboard._paste_html_clip_darwin()
        else:
            return Clipboard._paste_html_clip_linux()

    @staticmethod
    def _finalize_html_clipboard_payload(html_data) -> str:
        """
        各平台取到的 HTML 原始数据：统一解析片段、file 协议图片转 base64；
        无有效 HTML 则退回 pyperclip 纯文本。
        """
        if not html_data:
            return Clipboard.paste_str_clip()
        html_fragment = Clipboard._extract_html_fragment(html_data)
        if html_fragment:
            pattern = r'src="file:///(.*?\.(?:jpg|png|gif))"'
            matches = re.findall(pattern, html_fragment)
            for match in matches:
                base64_str = Clipboard._base64_encode(Base64CodeType.PICTURE, "", match)
                html_fragment = html_fragment.replace(r"file:///" + match, base64_str)
            return html_fragment
        return html_data if isinstance(html_data, str) else html_data.decode("utf-8", errors="replace")

    @staticmethod
    def _paste_html_clip_win32() -> str:
        import win32clipboard as cp

        html_data = ""
        cp.OpenClipboard()
        try:
            CF_HTML = cp.RegisterClipboardFormat("HTML Format")
            if cp.IsClipboardFormatAvailable(CF_HTML):
                html_data = cp.GetClipboardData(CF_HTML)
        except Exception:
            pass
        finally:
            cp.CloseClipboard()
        return Clipboard._finalize_html_clipboard_payload(html_data)

    @staticmethod
    def _paste_html_clip_darwin() -> str:
        script = r"""
ObjC.import("AppKit");
var pb = $.NSPasteboard.generalPasteboard;
var html = pb.stringForType("public.html");
if (html && html.length) { return ObjC.unwrap(html); }
var plain = pb.stringForType("public.utf8-plain-text");
return plain ? ObjC.unwrap(plain) : "";
"""
        try:
            result = subprocess.run(
                ["/usr/bin/osascript", "-l", "JavaScript", "-e", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                return Clipboard._finalize_html_clipboard_payload(result.stdout)
        except Exception:
            pass
        return Clipboard.paste_str_clip()

    @staticmethod
    def _paste_html_clip_linux() -> str:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o", "-t", "text/html"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return Clipboard._finalize_html_clipboard_payload(result.stdout)

    @staticmethod
    def _extract_html_fragment(html_clipboard_data):
        if isinstance(html_clipboard_data, str):
            html_clipboard_str = html_clipboard_data
        else:
            html_clipboard_str = html_clipboard_data.decode("utf-8")

        start_marker = "<!--StartFragment-->"
        end_marker = "<!--EndFragment-->"

        start_index = html_clipboard_str.find(start_marker)
        end_index = html_clipboard_str.find(end_marker)

        if start_index == -1 or end_index == -1:
            ms = re.search(r"StartHTML:(\d+)\r", html_clipboard_str)
            me = re.search(r"EndHTML:(\d+)\r", html_clipboard_str)
            if ms and me:
                return html_clipboard_str[int(ms.group(1)) : int(me.group(1))]
            return html_clipboard_str

        start_offset = start_index + len(start_marker)
        end_offset = end_index
        html_fragment = html_clipboard_str[start_offset:end_offset]
        return html_fragment

    @staticmethod
    def _base64_encode(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ) -> str:
        import base64

        if file_path:
            with open(file_path, "rb") as file:
                input_content = file.read()
        else:
            input_content = string_data.encode("utf-8")
        base64_encoded = base64.b64encode(input_content)
        base64_encode_result = base64_encoded.decode("utf-8")
        if encode_type == Base64CodeType.PICTURE:
            base64_encode_result = "data:image/png;base64," + base64_encode_result
        return base64_encode_result
