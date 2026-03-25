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

    def rect(self) -> Rect:   # ← 关键修复：永远返回 Rect，不再返回 None
        if self.__rect is None:
            r = _ax_element_rect(self.__element)
            if r is None:
                logger.warning(f"[AX Highlight Fix] _ax_element_rect 返回 None，强制使用 dummy Rect(0,0,0,0)")
                x, y, w, h = 0, 0, 0, 0
            else:
                x, y, w, h = r

            # 边界修正（保持你原来的逻辑）
            screen_w, screen_h = pyautogui.size()
            left = max(1, int(x))
            top = max(1, int(y))
            right = min(int(x + w), screen_w - 1)
            bottom = min(int(y + h), screen_h - 1)

            # 如果修正后宽高 <=0，也强制给一个最小矩形，避免高亮崩溃
            if right <= left or bottom <= top:
                logger.warning(f"[AX Highlight Fix] 修正后矩形无效 ({left},{top},{right},{bottom})，强制 dummy Rect")
                left, top, right, bottom = 0, 0, 10, 10

            self.__rect = Rect(left, top, right, bottom)
            logger.debug(f"[AX Highlight Fix] 最终 rect = {self.__rect} {left},{top},{right},{bottom}")
        return self.__rect

    def control(self) -> Any:
        return self.__element


# ── AXUIFactory（保持你之前的增强版 + 高亮无关） ─────────────────────────────

class AXUIFactory:
    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[list[AXUILocator], AXUILocator, None]:
        from ApplicationServices import AXUIElementCreateApplication

        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return None

        pids = cls._find_pids_by_name(app_name)
        logger.info(f"AXUIFactory.find: app={app_name}, pids={pids}, path_len={len(path_list)}")
        logger.debug(f"完整 ele 字典: {ele}")

        if not pids:
            raise BizException(NO_FIND_ELEMENT, f"找不到应用: {app_name}")

        for pid in pids:
            try:
                root = AXUIElementCreateApplication(pid)
                if root is None:
                    logger.warning(f"AXUIElementCreateApplication({pid}) 返回 None")
                    continue

                logger.debug(f"成功创建 root (pid={pid})")

                if picker_type == PickerType.WINDOW.value:
                    logger.info("PickerType.WINDOW，直接返回 root")
                    return AXUILocator(root)

                search_list = [(root, "1")]
                element_found = True
                current_level = 1

                for node_idx, node_dict in enumerate(path_list[1:], start=1):
                    if not node_dict.get("checked", True):
                        logger.debug(f"第 {node_idx} 层节点 checked=False，跳过")
                        continue

                    disable_keys = node_dict.get("disable_keys", [])
                    tag_name = node_dict.get("tag_name") if "tag_name" not in disable_keys else None
                    cls_name = node_dict.get("cls") if "cls" not in disable_keys else None
                    name = node_dict.get("name") if "name" not in disable_keys else None
                    value = node_dict.get("value") if "value" not in disable_keys else None
                    expected_idx = node_dict.get("index") if "index" not in disable_keys else None

                    logger.debug(f"第 {current_level} 层匹配条件 → tag={tag_name}, cls={cls_name}, "
                                 f"name={name}, value={value}, index={expected_idx}")

                    next_list = []
                    for parent_el, parent_sort in search_list:
                        children = _ax_attr(parent_el, "AXChildren") or []
                        logger.debug(f"  父节点有 {len(children)} 个子元素")
                        for child_idx, child in enumerate(children):
                            if cls._match_child(child, tag_name, cls_name, name, value, node_dict.get("attrs_map")):
                                index_ok = expected_idx is None or child_idx == expected_idx
                                sort_str = parent_sort + ("1" if index_ok else "0")
                                next_list.append((child, sort_str))
                                logger.debug(f"    ✓ 命中子元素 idx={child_idx} sort={sort_str}")

                    if not next_list:
                        logger.warning(f"✗ 第 {current_level} 层匹配失败！没有找到任何符合条件的子元素")
                        element_found = False
                        break

                    search_list = next_list
                    current_level += 1

                if element_found and search_list:
                    search_list.sort(key=lambda x: -int(x[1]))
                    best = search_list[0][0]
                    logger.info(f"✓ 找到元素 (best sort={search_list[0][1]})")
                    return AXUILocator(best)

                logger.debug(f"PID {pid} 路径遍历失败，继续下一个 PID")

            except Exception as e:
                logger.error(f"AXUIFactory.find: PID {pid} 异常: {e}", exc_info=True)
                continue

        raise BizException(NO_FIND_ELEMENT, "元素无法找到")

    @classmethod
    def _find_pids_by_name(cls, app_name: str) -> list:
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
        from astronverse.locator.utils.match import MatchType, match_value
        attrs_map = attrs_map or {}

        role = _ax_attr(el, "AXRole") or ""
        subrole = _ax_attr(el, "AXSubrole") or ""
        title = _ax_attr(el, "AXTitle") or ""
        ax_val = _ax_attr(el, "AXValue")
        ax_val_str = str(ax_val).strip() if ax_val is not None else ""

        logger.debug(f"    检查子元素: Role={role}, Subrole={subrole}, Title={title}, Value={ax_val_str}")

        if tag_name is not None:
            if not match_value(tag_name, role, attrs_map.get("tag_name", MatchType.EXACT)):
                return False
        if cls_name is not None:
            if not match_value(cls_name, subrole, attrs_map.get("cls", MatchType.EXACT)):
                return False
        if name is not None and name != "":
            if not match_value(name, title, attrs_map.get("name", MatchType.EXACT)):
                return False
        if value is not None:
            if not match_value(str(value), ax_val_str, attrs_map.get("value", MatchType.EXACT)):
                return False
        return True


axui_factory = AXUIFactory()