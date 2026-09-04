import os
import time
from typing import Any
from astronverse.browser import BROWSER_UIA_WINDOW_CLASS, BROWSER_REGISTER_NAME, BROWSER_UIA_POINT_CLASS
from astronverse.browser.error import DOWNLOAD_WINDOW_NO_FIND, UPLOAD_WINDOW_NO_FIND


class BrowserCore:
    @staticmethod
    def get_browser_path(browser_type: str) -> str:
        """获取浏览器绝对地址"""
        app_name = BROWSER_REGISTER_NAME.get(browser_type, "")
        if not app_name:
            return ""
        from astronverse.software.software import Software

        return Software.get_app_path(app_name)

    @staticmethod
    def browser_top_and_max(control):
        from astronverse.window import WindowSizeType
        from astronverse.window.window import WindowsCore
        from astronverse.window.uitree import UITreeCore

        handler = UITreeCore.toHandler(control)
        WindowsCore.top(handler)
        WindowsCore.size(handler, WindowSizeType.MAX)

    @staticmethod
    def get_browser_point(browser_type: str) -> Any:
        """获取浏览器坐标"""

        base_ctrl = BrowserCore.get_browser_control(browser_type)
        if not base_ctrl:
            return None

        cfg = BROWSER_UIA_POINT_CLASS.get(browser_type)
        if not cfg:
            return None

        tag_value, tag = cfg

        from astronverse.window.uitree import UITreeCore
        from astronverse.window import WalkControlInfo

        for walkControlInfo in UITreeCore.WalkControl(base_ctrl, True, 12):
            assert isinstance(walkControlInfo, WalkControlInfo)
            if tag == "ClassName":
                tag_match = walkControlInfo.classname
            elif tag == "AutomationId":
                tag_match = walkControlInfo.automation_id
            else:
                tag_match = ""
            if tag_match == tag_value:
                bounding_rect = walkControlInfo.position
                top = bounding_rect.top
                left = bounding_rect.left
                return top, left

    @staticmethod
    def get_browser_control(browser_type: str) -> Any:
        """获取浏览器的控制器"""

        cfg = BROWSER_UIA_WINDOW_CLASS.get(browser_type)
        if not cfg:
            return None

        from astronverse.window.uitree import UITreeCore
        from astronverse.window import WalkControlInfo

        class_name, patterns, match_type = cfg
        root_control = UITreeCore.GetRootControl()
        control = None
        for info in UITreeCore.WalkControl(root_control, True, 1):
            assert isinstance(info, WalkControlInfo)
            if info.classname != class_name:
                continue
            if not patterns:
                control = info.control
                break
            text = info.name.split("-")[-1].strip() if match_type == "last_in" else info.name
            if any(p.lower() in text.lower() for p in patterns):
                control = info.control
                break
        return control

    @staticmethod
    def download_window_operate(**kwargs) -> Any:
        """获取浏览器下载文件另存为窗口"""

        import win32con
        import win32gui

        file_name = kwargs.get("file_name")
        browser_type = kwargs.get("browser_type")
        is_wait = kwargs.get("is_wait")
        time_out = kwargs.get("time_out")

        def get_text_from_edit(hwnd):
            # 获取edit控件的文本长度
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) * 2 + 2
            # 创建缓冲区并发送WM_GETTEXT消息获取文本
            buffer = win32gui.PyMakeBuffer(length)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length, buffer)
            address, result_length = win32gui.PyGetBufferAddressAndLen(buffer)
            text = win32gui.PyGetString(address, result_length // 2 - 1)
            return text

        # 判断是否弹出下载窗口
        # 「另存为」对话框标题随系统语言变化（issue #791）：
        # 中文为「另存为」，英文为「Save As」，日文为「名前を付けて保存」等，
        # 依次尝试各语言标题，避免在非中文 Windows 上找不到窗口。
        save_as_titles = ["另存为", "另存新檔", "Save As", "名前を付けて保存", "다른 이름으로 저장"]

        def find_dialog():
            for title in save_as_titles:
                hwnd = win32gui.FindWindow("#32770", title)  # 一级窗口
                if hwnd:
                    return hwnd
            return 0

        dialog = find_dialog()
        start_time = time.time()
        while time.time() - start_time < 10:
            dialog = find_dialog()
            if dialog == 0:
                time.sleep(0.1)
            else:
                time.sleep(3)
                break
        if dialog == 0:
            raise BaseException(DOWNLOAD_WINDOW_NO_FIND, "未弹出下载窗口")

        # 查找到edit， button
        # 「保存(S)」按钮文案随语言变化，改用标准文件对话框默认按钮的控件 ID
        # （IDOK=1，与下方 WM_COMMAND 的 wParam 一致），不依赖按钮文案；
        # 取不到再回退到按标题查找，兼容非标准对话框。
        button = win32gui.GetDlgItem(dialog, win32con.IDOK)
        if not button:
            for _caption in ("保存(S)", "保存", "Save", "저장(S)"):
                button = win32gui.FindWindowEx(dialog, 0, "Button", _caption)
                if button:
                    break

        a1 = win32gui.FindWindowEx(dialog, None, "DUIViewWndClassName", None)
        a2 = win32gui.FindWindowEx(a1, None, "DirectUIHWND", None)
        a3 = win32gui.FindWindowEx(a2, None, "FloatNotifySink", None)
        a4 = win32gui.FindWindowEx(a3, None, "ComboBox", None)
        edit = win32gui.FindWindowEx(a4, None, "Edit", None)
        origin_name = get_text_from_edit(edit)
        if origin_name.find(".") != -1:
            name = origin_name.split(".")[0]
            suffix = origin_name.rsplit(".", 1)[-1]
            if not suffix.isalpha():
                name = origin_name
                suffix = ""
        else:
            name = origin_name
            suffix = ""

        # 往编辑当中，输入文件路径
        if kwargs.get("custom_flag"):
            name = file_name

        if suffix:
            dest_path = os.path.join(kwargs.get("save_path"), name + "." + suffix)
        else:
            dest_path = os.path.join(kwargs.get("save_path"), name)

        # 直接向 Edit 控件句柄写入路径，避免经由系统剪贴板 + Ctrl+V：
        # 剪贴板是全局共享资源，粘贴依赖窗口焦点，二者在人工辅助、
        # 多机器人并发或前台窗口切换时会互相污染 / 抢焦点（见 issue #795）。
        # upload_window_operate 已采用同样的 WM_SETTEXT 直写方式。
        win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, dest_path)  # 写入文件路径
        time.sleep(0.5)
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击保存按钮

        if is_wait:
            if not (time_out == 0 or time_out == ""):
                try:
                    wait_time_download = int(time_out)
                except Exception:
                    wait_time_download = 60
                while wait_time_download > 0:
                    wait_time_download = wait_time_download - 3
                    if os.path.exists(dest_path):
                        break
                    time.sleep(3)
                if wait_time_download <= 0 and not os.path.exists(dest_path):
                    raise Exception("等待下载完成超时")
        return dest_path

    @staticmethod
    def upload_window_operate(**kwargs) -> Any:
        """获取浏览器上传文件窗口操作"""

        import win32con
        import win32gui

        upload_path = kwargs.get("upload_path")
        browser_type = kwargs.get("browser_type")

        # 判断是否弹出上传窗口
        # 「打开」对话框标题随系统语言变化（issue #791），依次尝试各语言标题。
        open_titles = ["打开", "開啟", "Open", "開く", "열기"]

        def find_dialog():
            for title in open_titles:
                hwnd = win32gui.FindWindow("#32770", title)  # 一级窗口
                if hwnd:
                    return hwnd
            return 0

        dialog = find_dialog()
        start_time = time.time()
        while time.time() - start_time < 10:
            dialog = find_dialog()
            if dialog == 0:
                time.sleep(0.1)
            else:
                time.sleep(3)
                break
        if dialog == 0:
            raise BaseException(UPLOAD_WINDOW_NO_FIND, "未弹出上传窗口")

        # 「打开(O)」按钮文案随语言变化，改用默认按钮控件 ID（IDOK=1），
        # 回退到按标题查找。
        button = win32gui.GetDlgItem(dialog, win32con.IDOK)  # 四级
        if not button:
            for _caption in ("打开(O)", "打开", "Open", "열기(O)"):
                button = win32gui.FindWindowEx(dialog, 0, "Button", _caption)
                if button:
                    break

        a1 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)  # 二级
        a2 = win32gui.FindWindowEx(a1, 0, "ComboBox", None)  # 三级
        edit = win32gui.FindWindowEx(a2, 0, "Edit", None)  # 四级

        # 往编辑当中，输入文件路径。
        dest_path = ""
        if upload_path.find("|") != -1:
            upload_path = upload_path.split("|")
        if type(upload_path) == list:
            for file in upload_path:
                dest_path += f'"{file.strip()}" '
        else:
            dest_path = upload_path

        win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, dest_path)  # 发送文件路径
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击打开按钮
