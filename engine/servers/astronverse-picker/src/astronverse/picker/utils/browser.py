from typing import Any
from urllib.parse import urljoin
from astronverse.picker.logger import logger
import requests
import uiautomation as auto
from typing import Optional, Set, List
import psutil
import ctypes
from ctypes import wintypes
import time

# --- Win32 API 初始化 (全局加载一次) ---
user32 = ctypes.windll.user32

from astronverse.picker.error import (
    BROWSER_EXTENSION_INSTALL_ERROR,
    BROWSER_EXTENSION_ERROR_FORMAT,
    WEB_GET_ElE_ERROR,
    WEB_EXEC_ElE_ERROR,
)


class Browser:
    """浏览器操作类"""

    @staticmethod
    def send_browser_rpc(req: dict, timeout: float = None, gateway_port=8003) -> Any:
        """发送浏览器RPC请求。"""
        url = f"http://127.0.0.1:{gateway_port}"
        return requests.post(
            urljoin(
                url,
                "browser_connector",
            )
            + "/browser/transition",
            json=req,
            timeout=timeout,
        )

    @staticmethod
    def send_browser_extension(
        browser_type: str, data: Any, key: str, gate_way_port: int, data_path: str = "", timeout: float = None
    ):
        """发送浏览器扩展请求。"""
        max_retries = 3
        retry_interval = 0.5  # 每次重试间隔，可根据实际情况调整

        for attempt in range(1, max_retries + 1):
            response = Browser.send_browser_rpc(
                {
                    "browser_type": browser_type,
                    "data": data,
                    "key": key,
                    "data_path": data_path,
                },
                timeout,
                gateway_port=gate_way_port,
            )

            if response.status_code != 200:
                raise Exception("浏览器插件连接器通信通道出错，请重试")

            res_json = response.json()
            res_code = res_json.get("code")
            res_data = res_json.get("data") or {}
            res_msg = res_data.get("msg")

            # 如果是1001，则最多重试3次
            if res_code == "1001":
                if attempt < max_retries:
                    time.sleep(retry_interval)
                    continue
                else:
                    raise Exception(f"[{browser_type}] 浏览器插件响应出错，请检查插件是否安装并已开启")

            # 插件返回错误
            if res_code != "0000":
                raise Exception(f"[{browser_type}] {res_msg}")

            if not res_data:
                return None

            data_code = res_data.get("code")
            data_msg = res_data.get("msg", "")

            # 定义错误码与对应异常映射表
            error_map = {
                "5001": (BaseException, BROWSER_EXTENSION_ERROR_FORMAT, data_msg),
                "5002": (BaseException, WEB_GET_ElE_ERROR, data_msg),
                "5003": (BaseException, WEB_EXEC_ElE_ERROR, data_msg),
                "5004": (Exception, BROWSER_EXTENSION_ERROR_FORMAT, data_msg),
            }

            if data_code in error_map and key not in ["getElement"]:
                _, _, fallback_msg = error_map[data_code]
                raise Exception(fallback_msg)

            return res_data.get("data", "")

        # 理论上不会走到这里
        return None


class BrowserControlFinder:
    """根据应用名称查找对应的UIA控件 (经过 Win32 API 深度优化版)"""

    # 进程名称映射
    PROCESS_MAP = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "iexplore": "iexplore.exe",
        "firefox": "firefox.exe",
        "360chromex": "360chromex.exe",
        "360se": "360se.exe",
        "360chrome": "360chrome.exe",
        "chromium": "chromium.exe",
    }

    # 浏览器窗口ClassName映射
    CLASS_NAME_MAP = {
        "chrome": "Chrome_WidgetWin_1",
        "edge": "Chrome_WidgetWin_1",
        "firefox": "MozillaWindowClass",
        "iexplore": "IEFrame",
        "360chromex": "Chrome_WidgetWin_1",
        "360se": "Chrome_WidgetWin_1",
        "360chrome": "Chrome_WidgetWin_1",
        "chromium": "Chrome_WidgetWin_1",
    }

    @staticmethod
    def _get_hwnds_by_pid(target_pid: int) -> List[int]:
        """
        【核心优化】使用 Win32 API 快速获取指定 PID 的所有 *可见* 顶层窗口句柄
        """
        hwnds = []

        def callback(hwnd, _):
            # 1. 获取窗口所属的进程ID
            window_pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))

            if window_pid.value == target_pid:
                # 2. 【关键过滤】只获取可见窗口。
                # 浏览器会在后台创建大量不可见窗口，过滤它们能极大提升性能。
                if user32.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
            return True

        # 定义回调函数类型
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(callback), 0)
        return hwnds

    @classmethod
    def _get_process_ids(cls, process_name: str) -> Set[int]:
        """获取所有匹配的进程ID集合"""
        pids = set()
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"] and proc.info["name"].lower() == process_name.lower():
                        pids.add(proc.info["pid"])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"获取进程ID失败: {e}")
        return pids

    @classmethod
    def get_control_by_app_name(cls, app_name: str, window_title: str = None) -> Optional[auto.Control]:
        """
        获取主窗口控件 - 极致性能版
        """
        app_key = app_name.lower()
        process_name = cls.PROCESS_MAP.get(app_key)
        expected_class_name = cls.CLASS_NAME_MAP.get(app_key)

        if not process_name:
            print(f"不支持的应用名称: {app_name}")
            return None

        target_pids = cls._get_process_ids(process_name)
        if not target_pids:
            return None

        matched_controls = []

        # --- 优化逻辑开始 ---
        for pid in target_pids:
            # 1. 极速获取句柄 (跳过 UIA 树遍历)
            hwnds = cls._get_hwnds_by_pid(pid)

            for hwnd in hwnds:
                try:
                    # 2. 句柄转对象 (无搜索开销)
                    control = auto.ControlFromHandle(hwnd)

                    # 3. 检查 ClassName (本地属性，快)
                    if expected_class_name:
                        if control.ClassName != expected_class_name:
                            continue

                    # 4. 匹配标题
                    if window_title:
                        # 只有在最后一步才去获取 Name，因为字符串操作相对较慢
                        if window_title in control.Name:
                            return control
                    else:
                        # 暂存备选
                        matched_controls.append(control)

                except Exception:
                    # 窗口可能在枚举间隙被关闭
                    continue

        # --- 后备选择 ---
        # 如果没有指定标题，返回第一个可用的窗口
        if matched_controls:
            for control in matched_controls:
                if control.IsEnabled:
                    return control
            return matched_controls[0]

        return None

    @staticmethod
    def _find_document_control_recursive(
        control: auto.Control, parent_name: str, depth: int = 0, max_depth: int = 20
    ) -> Optional[auto.Control]:
        """
        递归查找ControlType为Document的同名子节点 (保持原样)
        """
        if depth > max_depth:
            return None

        try:
            if control.ControlType == auto.ControlType.DocumentControl:
                return control

            children = control.GetChildren()
            for child in children:
                try:
                    result = BrowserControlFinder._find_document_control_recursive(
                        child, parent_name, depth + 1, max_depth
                    )
                    if result:
                        return result
                except:
                    continue
        except Exception:
            pass
        return None

    @staticmethod
    def get_document_control(parent_control: auto.Control) -> Optional[auto.Control]:
        """获取父控件下name相同且ControlType为Document的子孙节点 (保持原样)"""
        if not parent_control:
            return None

        try:
            parent_name = parent_control.Name
            if not parent_name:
                return None

            children = parent_control.GetChildren()
            for child in children:
                try:
                    result = BrowserControlFinder._find_document_control_recursive(child, parent_name)
                    if result:
                        return result
                except:
                    continue

        except Exception as e:
            print(f"查找Document控件失败: {e}")

        return None


# 使用示例
if __name__ == "__main__":
    print("正在查找窗口...")
    start = time.perf_counter()

    # 示例: 查找 Chrome 窗口 (你可以打开 Chrome 测试)
    # 如果想测试标题匹配，可以传入第二个参数，例如: "百度"
    chrome_control = BrowserControlFinder.get_control_by_app_name("Chrome")

    end1 = time.perf_counter()
    print(f"查找顶层窗口耗时: {(end1 - start) * 1000:.2f} ms")  # 应该是毫秒级

    if chrome_control:
        print(f"找到匹配窗口: {chrome_control.Name} | Handle: {hex(chrome_control.NativeWindowHandle)}")

        # 获取 Document 区域 (这部分是递归查找，仍然会消耗一些时间)
        doc_start = time.perf_counter()
        doc_control = BrowserControlFinder.get_document_control(chrome_control)
        doc_end = time.perf_counter()

        if doc_control:
            print(f"找到Document控件: {doc_control.BoundingRectangle}")
        else:
            print("未找到Document控件")

        print(f"查找内部Document耗时: {doc_end - doc_start:.4f} 秒")

    else:
        print("未找到指定应用的窗口")
