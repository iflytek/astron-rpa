# macOS implementation - AXUIElement based locator
# Replaces both uia_locator.py and msaa_locator.py on macOS.
import ctypes
from typing import Any, Optional, Union

import pyautogui
from ApplicationServices import (
    AXUIElementCopyAttributeValue,
    AXUIElementGetPid,
    kAXErrorSuccess,
)
import ApplicationServices as AS

from astronverse.baseline.logger.logger import logger
from astronverse.locator import ILocator, PickerType, Rect
from astronverse.locator.error import BizException, NO_FIND_ELEMENT


# ── AX 工具函数 ─────────────────────────────────────────────────────────────


def _ax_attr(el, attr):
    try:
        err, val = AXUIElementCopyAttributeValue(el, attr, None)
        return val if err == kAXErrorSuccess else None
    except Exception:
        return None


def _ax_unpack_rect(val):
    try:
        ok, rect = AS.AXValueGetValue(val, AS.kAXValueCGRectType, None)
        if ok and rect is not None:
            return rect.origin.x, rect.origin.y, rect.size.width, rect.size.height
    except Exception:
        pass
    return None


def _ax_unpack_point(val):
    try:
        ok, pt = AS.AXValueGetValue(val, AS.kAXValueCGPointType, None)
        if ok and pt is not None:
            return pt.x, pt.y
    except Exception:
        pass
    return None


def _ax_unpack_size(val):
    try:
        ok, sz = AS.AXValueGetValue(val, AS.kAXValueCGSizeType, None)
        if ok and sz is not None:
            return sz.width, sz.height
    except Exception:
        pass
    return None


def _ax_element_rect(el) -> Optional[tuple]:
    """返回 (x, y, w, h)，失败返回 None"""
    frame_v = _ax_attr(el, "AXFrame")
    if frame_v is not None:
        r = _ax_unpack_rect(frame_v)
        if r and r[2] > 0 and r[3] > 0:
            return r
    pv = _ax_attr(el, "AXPosition")
    sv = _ax_attr(el, "AXSize")
    if pv is None or sv is None:
        return None
    pt = _ax_unpack_point(pv)
    sz = _ax_unpack_size(sv)
    if pt and sz and sz[0] > 0 and sz[1] > 0:
        return pt[0], pt[1], sz[0], sz[1]
    return None


def _ax_get_pid(el) -> int:
    try:
        pid = ctypes.c_int(0)
        AXUIElementGetPid(el, ctypes.byref(pid))
        return pid.value
    except Exception:
        return 0


# ── AXUILocator ─────────────────────────────────────────────────────────────


class AXUILocator(ILocator):
    """macOS AXUIElement 定位器，替代 UIALocator 和 MSAALocator"""

    def __init__(self, element: Any):
        self.__element = element
        self.__rect = None

    def rect(self) -> Optional[Rect]:
        if self.__rect is None:
            r = _ax_element_rect(self.__element)
            if r is None:
                return None
            x, y, w, h = r
            # 边界修正（对应 UIALocator 的 pyautogui.size() 修正逻辑）
            screen_w, screen_h = pyautogui.size()
            left = max(1, int(x))
            top = max(1, int(y))
            right = min(int(x + w), screen_w - 1)
            bottom = min(int(y + h), screen_h - 1)
            self.__rect = Rect(left, top, right, bottom)
        return self.__rect

    def control(self) -> Any:
        return self.__element


# ── AXUIFactory ─────────────────────────────────────────────────────────────


class AXUIFactory:
    """macOS AXUIElement 工厂，统一处理 UIA 和 MSAA domain 的定位请求"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[list[AXUILocator], AXUILocator, None]:
        """基于 AXUIElement 的元素查找。

        算法：
          1. 通过 app_name 找到所有匹配进程的 PID
          2. 用 AXUIElementCreateApplication(pid) 获取 AX 根节点
          3. 跳过 path_list[0]（应用根节点），从 path_list[1:] 开始逐层匹配
          4. 硬匹配：tag_name(AXRole) / cls(AXSubrole) / name(AXTitle) / value(AXValue)
          5. 软匹配：index（优先选 index 匹配的，但不强制）
        """
        from ApplicationServices import AXUIElementCreateApplication

        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return None

        pids = cls._find_pids_by_name(app_name)
        if not pids:
            raise BizException(NO_FIND_ELEMENT, f"找不到应用: {app_name}")

        logger.info(f"AXUIFactory.find: app={app_name}, pids={pids}, path_len={len(path_list)}")

        for pid in pids:
            try:
                root = AXUIElementCreateApplication(pid)
                if root is None:
                    continue

                if picker_type == PickerType.WINDOW.value:
                    return AXUILocator(root)

                # (ax_element, index_match_sort_str)
                search_list = [(root, "1")]
                element_found = True

                for node_dict in path_list[1:]:
                    if not node_dict.get("checked", True):
                        continue

                    disable_keys = node_dict.get("disable_keys", [])
                    tag_name = node_dict.get("tag_name") if "tag_name" not in disable_keys else None
                    cls_name = node_dict.get("cls") if "cls" not in disable_keys else None
                    name = node_dict.get("name") if "name" not in disable_keys else None
                    value = node_dict.get("value") if "value" not in disable_keys else None
                    expected_idx = node_dict.get("index") if "index" not in disable_keys else None
                    attrs_map = node_dict.get("attrs_map", {})

                    next_list = []
                    for parent_el, parent_sort in search_list:
                        children = _ax_attr(parent_el, "AXChildren") or []
                        for child_idx, child in enumerate(children):
                            if not cls._match_child(child, tag_name, cls_name, name, value, attrs_map):
                                continue
                            index_ok = expected_idx is None or child_idx == expected_idx
                            next_list.append((child, parent_sort + ("1" if index_ok else "0")))

                    if not next_list:
                        element_found = False
                        break
                    search_list = next_list

                if element_found and search_list:
                    search_list.sort(key=lambda x: -int(x[1]))
                    return AXUILocator(search_list[0][0])

            except Exception as e:
                logger.debug(f"AXUIFactory.find: PID {pid} 处理失败: {e}")
                continue

        raise BizException(NO_FIND_ELEMENT, "元素无法找到")

    @classmethod
    def _find_pids_by_name(cls, app_name: str) -> list:
        """通过进程名找所有匹配的 PID（精确 + 大小写不敏感）"""
        pids = []
        try:
            import psutil

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    proc_name = proc.info.get("name", "") or ""
                    base_name = proc_name.rsplit(".", 1)[0] if "." in proc_name else proc_name
                    if app_name.lower() in (proc_name.lower(), base_name.lower()):
                        pids.append(proc.info["pid"])
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"psutil 查找进程失败: {e}")
        return pids

    @classmethod
    def _match_child(cls, el, tag_name, cls_name, name, value, attrs_map) -> bool:
        """硬匹配：检查 AX 元素的 Role/Subrole/Title/Value 是否符合节点要求"""
        from astronverse.locator.utils.match import MatchType, match_value

        attrs_map = attrs_map or {}

        if tag_name is not None:
            role = _ax_attr(el, "AXRole") or ""
            if not match_value(tag_name, role, attrs_map.get("tag_name", MatchType.EXACT)):
                return False

        if cls_name is not None:
            subrole = _ax_attr(el, "AXSubrole") or ""
            if not match_value(cls_name, subrole, attrs_map.get("cls", MatchType.EXACT)):
                return False

        if name is not None and name != "":
            title = _ax_attr(el, "AXTitle") or ""
            if not match_value(name, title, attrs_map.get("name", MatchType.EXACT)):
                return False

        if value is not None:
            ax_val = _ax_attr(el, "AXValue")
            ax_val_str = str(ax_val).strip() if ax_val is not None else ""
            if not match_value(str(value), ax_val_str, attrs_map.get("value", MatchType.EXACT)):
                return False

        return True


axui_factory = AXUIFactory()
