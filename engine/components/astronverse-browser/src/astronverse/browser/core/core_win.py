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

        import pyperclip
        import win32con
        import pyautogui
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
        dialog = win32gui.FindWindow("#32770", "另存为")  # 一级窗口
        start_time = time.time()
        while time.time() - start_time < 10:
            dialog = win32gui.FindWindow("#32770", "另存为")  # 一级窗口
            if dialog == 0:
                time.sleep(0.1)
            else:
                time.sleep(3)
                break
        if dialog == 0:
            raise BaseException(DOWNLOAD_WINDOW_NO_FIND, "未弹出下载窗口")

        # 查找到edit， button
        button = win32gui.FindWindowEx(dialog, 0, "Button", "保存(S)")

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
        pyperclip.copy(dest_path)

        # 等待一段时间，以确保字符串已复制到剪贴板
        time.sleep(0.5)

        # 模拟 Ctrl+V 粘贴操作
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击打开按钮

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
        dialog = win32gui.FindWindow("#32770", "打开")
        start_time = time.time()
        while time.time() - start_time < 10:
            dialog = win32gui.FindWindow("#32770", "打开")  # 一级窗口
            if dialog == 0:
                time.sleep(0.1)
            else:
                time.sleep(3)
                break
        if dialog == 0:
            raise BaseException(UPLOAD_WINDOW_NO_FIND, "未弹出上传窗口")

        button = win32gui.FindWindowEx(dialog, 0, "Button", "打开(O)")  # 四级

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
