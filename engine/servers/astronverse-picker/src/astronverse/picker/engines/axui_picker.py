# macOS implementation - based on ApplicationServices AXUIElement API
from typing import Any, Optional, List, Dict

import Quartz
from ApplicationServices import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyAttributeNames,
    AXUIElementCopyElementAtPosition,
    AXUIElementGetPid,
    kAXErrorSuccess,
)
import ApplicationServices as AS

from astronverse.picker import APP, IElement, PickerDomain, PickerType, Point, Rect
from astronverse.picker.logger import logger
from astronverse.picker.utils.cv import screenshot
from astronverse.picker.utils.process import get_process_name


# ── AX 工具函数 ─────────────────────────────────────────────────────────────

AX_DEBUG = True

def _ax_log(msg: str):
    if AX_DEBUG:
        logger.info(f"[AX] {msg}")


def _ax_attr(el, attr):
    try:
        err, val = AXUIElementCopyAttributeValue(el, attr, None)
        return val if err == kAXErrorSuccess else None
    except Exception:
        return None


def _ax_attr_names(el) -> List[str]:
    try:
        err, names = AXUIElementCopyAttributeNames(el, None)
        return list(names) if err == kAXErrorSuccess and names else []
    except Exception:
        return []


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


def _ax_unpack_rect(val):
    try:
        ok, rect = AS.AXValueGetValue(val, AS.kAXValueCGRectType, None)
        if ok and rect is not None:
            return rect.origin.x, rect.origin.y, rect.size.width, rect.size.height
    except Exception:
        pass
    return None


def _ax_element_rect(el) -> Optional[tuple]:
    frame_v = _ax_attr(el, "AXFrame")
    if frame_v is not None:
        rect = _ax_unpack_rect(frame_v)
        if rect and rect[2] > 0 and rect[3] > 0:
            _ax_log(f"rect(AXFrame)={rect}")
            return rect

    pv = _ax_attr(el, "AXPosition")
    sv = _ax_attr(el, "AXSize")
    if pv is None or sv is None:
        _ax_log("rect: missing pos/size")
        return None

    pt = _ax_unpack_point(pv)
    sz = _ax_unpack_size(sv)
    if pt and sz and sz[0] > 0 and sz[1] > 0:
        rect = (pt[0], pt[1], sz[0], sz[1])
        _ax_log(f"rect(pos/size)={rect}")
        return rect

    _ax_log("rect: invalid")
    return None


def _ax_to_rect(el) -> Optional[Rect]:
    r = _ax_element_rect(el)
    if r is None:
        return None
    x, y, w, h = r
    return Rect(int(x), int(y), int(x + w), int(y + h))


def _ax_get_pid_raw(el) -> int:
    """
    直接从单个 AX 元素读取 PID。

    PyObjC 的 AXUIElementGetPid 绑定接受两个参数（element, pid_t*），
    但在不同 PyObjC 版本下 out-param 传递方式不同。
    这里用两种方式依次尝试，避免 ctypes/PyObjC 混用的坑。
    """
    # 方式一：PyObjC 原生 out-param（某些版本返回 (err, pid) 元组）
    try:
        result = AXUIElementGetPid(el, None)
        if isinstance(result, (tuple, list)) and len(result) == 2:
            err, pid = result
            if err == kAXErrorSuccess and isinstance(pid, int) and pid > 1:
                return pid
    except Exception:
        pass

    # 方式二：ctypes byref（另一些版本需要显式传指针）
    try:
        import ctypes
        pid = ctypes.c_int32(0)
        err = AXUIElementGetPid(el, ctypes.byref(pid))
        if err == kAXErrorSuccess and pid.value > 1:
            return pid.value
    except Exception:
        pass

    return 0


def _ax_get_pid(el) -> int:
    """
    可靠地获取 AX 元素所属进程的 PID。

    策略：
    1. 沿祖先链向上找到 AXApplication 节点，在该节点调用 AXUIElementGetPid。
       AXApplication 层级的 PID 最稳定，不会出现子元素归属混乱的问题。
    2. 若爬链失败或仍得到无效 PID，直接在原始元素上尝试一次。
    """
    # 步骤 1：向上爬到 AXApplication
    cur = el
    visited = 0
    while cur is not None and visited < 64:  # 防止死循环
        visited += 1
        role = _ax_attr(cur, "AXRole")
        if role == "AXApplication":
            pid = _ax_get_pid_raw(cur)
            if pid > 1:
                _ax_log(f"_ax_get_pid: found AXApplication, pid={pid}")
                return pid
            # AXApplication 取到无效值，不再往上爬，直接跳到步骤 2
            break
        parent = _ax_attr(cur, "AXParent")
        if parent is None:
            break
        cur = parent

    # 步骤 2：直接在原始元素上尝试
    pid = _ax_get_pid_raw(el)
    _ax_log(f"_ax_get_pid: fallback direct, pid={pid}")
    return pid


def _quartz_pid_at_point(x: float, y: float) -> int:
    """
    通过 Quartz 窗口列表查找坐标 (x, y) 处最顶层真实应用窗口的 PID。

    CGWindowListCopyWindowInfo 返回的列表按 Z 序从前到后排列，
    遍历找到第一个包含该点且属于普通应用层（layer < 25）的窗口即可。
    """
    try:
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly
            | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID,
        )
        for window in (window_list or []):
            # 跳过菜单栏、状态栏、Dock 等系统层（layer >= 25）
            layer = window.get("kCGWindowLayer", 999)
            if layer >= 25:
                continue
            bounds = window.get("kCGWindowBounds", {})
            wx = bounds.get("X", 0)
            wy = bounds.get("Y", 0)
            ww = bounds.get("Width", 0)
            wh = bounds.get("Height", 0)
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                pid = window.get("kCGWindowOwnerPID", 0)
                if pid > 1:
                    proc_name = get_process_name(pid)
                    if proc_name and proc_name.lower() not in ("kernel_task", ""):
                        _ax_log(
                            f"_quartz_pid_at_point: ({x},{y}) → pid={pid} ({proc_name})"
                        )
                        return pid
    except Exception as e:
        logger.warning(f"_quartz_pid_at_point error: {e}")
    return 0


def _ax_find_deepest_at_point(el, x, y, depth=0, max_depth=10):
    indent = "  " * depth
    if depth > max_depth:
        _ax_log(f"{indent}max depth reached")
        return el

    rect = _ax_element_rect(el)
    if rect is None:
        _ax_log(f"{indent}no rect")
        return el

    rx, ry, rw, rh = rect
    best = el
    best_area = rw * rh

    def contains(r):
        rx, ry, rw, rh = r
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    _ax_log(f"{indent}node rect={rect}")

    children = _ax_attr(el, "AXChildren") or []
    _ax_log(f"{indent}children={len(children)}")

    for i, child in enumerate(children):
        child_rect = _ax_element_rect(child)
        if child_rect is None:
            continue
        if not contains(child_rect):
            continue

        _ax_log(f"{indent} child[{i}] HIT {child_rect}")

        sub = _ax_find_deepest_at_point(child, x, y, depth + 1, max_depth)
        sub_rect = _ax_element_rect(sub)
        if sub_rect:
            area = sub_rect[2] * sub_rect[3]
            if area < best_area:
                best = sub
                best_area = area
    return best


def _ax_get_element_at(x: float, y: float) -> Optional[Any]:
    try:
        _ax_log(f"\n=== HIT TEST ({x},{y}) ===")
        sys_el = AXUIElementCreateSystemWide()
        err, el = AXUIElementCopyElementAtPosition(sys_el, float(x), float(y), None)

        if err == kAXErrorSuccess and el is not None:
            refined = _ax_find_deepest_at_point(el, x, y)
            role = _ax_attr(refined, "AXRole")
            title = _ax_attr(refined, "AXTitle") or _ax_attr(refined, "AXLabel")
            _ax_log(f"FINAL => role={role}, title={title}")
            return refined
    except Exception as e:
        logger.exception(f"_ax_get_element_at error: {e}")
    return None


def _ax_ancestor_chain(el) -> list:
    chain = []
    cur = el
    while cur is not None:
        chain.append(cur)
        parent = _ax_attr(cur, "AXParent")
        if parent is None:
            break
        cur = parent
    chain.reverse()
    return chain


# ── 属性收集（保持不变） ───────────────────────────────────────────────────

def _format_ax_value(attr: str, val) -> str:
    if val is None:
        return "None"
    if attr == "AXPosition":
        pt = _ax_unpack_point(val)
        return f"({pt[0]:.0f}, {pt[1]:.0f})" if pt else str(val)
    if attr == "AXSize":
        sz = _ax_unpack_size(val)
        return f"({sz[0]:.0f} × {sz[1]:.0f})" if sz else str(val)
    if isinstance(val, bool):
        return "✓" if val else "✗"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return val or "(empty)"
    if isinstance(val, (list, tuple)):
        return f"[{len(val)} items]"
    try:
        return str(val)
    except Exception:
        return "(unknown)"


def _collect_attrs(el) -> Dict[str, str]:
    PRIORITY = ["AXRole", "AXRoleDescription", "AXTitle", "AXLabel", "AXValue", "AXDescription", "AXHelp", "AXEnabled", "AXFocused", "AXSelected", "AXExpanded", "AXIdentifier", "AXPosition", "AXSize"]
    SKIP = {"AXChildren", "AXParent", "AXWindow", "AXTopLevelUIElement"}
    names = _ax_attr_names(el)
    result = {}
    for k in PRIORITY:
        if k in names:
            v = _ax_attr(el, k)
            if v is not None:
                result[k] = _format_ax_value(k, v)
    for k in names:
        if k not in PRIORITY and k not in SKIP:
            v = _ax_attr(el, k)
            if v is not None:
                result[k] = _format_ax_value(k, v)
    return result


# ── AXUIElement ─────────────────────────────────────────────────────────────

class AXUIElement(IElement):
    def __init__(self, element: Any):
        self.element = element
        self.__rect: Optional[Rect] = None
        self.__tag: Optional[str] = None
        self.__attributes: Optional[Dict[str, str]] = None
        self.__ancestor_chain: Optional[List['AXUIElement']] = None

    def rect(self) -> Rect:
        if self.__rect is None:
            r = _ax_to_rect(self.element)
            if r is None:
                r = Rect(0, 0, 0, 0)
            self.__rect = r
        return self.__rect

    def tag(self) -> str:
        if self.__tag is None:
            role = _ax_attr(self.element, "AXRole") or ""
            self.__tag = str(role).replace("AX", "")
        return self.__tag

    def path(self, svc=None, strategy_svc=None) -> dict:
        """已彻底修复 app 字段 + 通用 fallback"""
        chain = _ax_ancestor_chain(self.element)
        path_list = []

        # === 核心修复：通用 app_name 获取 ===
        app_pid = _ax_get_pid(chain[0]) if chain else 0
        app_name = get_process_name(app_pid)

        if app_pid == 0 or app_name.lower() == "kernel_task" or not app_name:
            app_title = _ax_attr(chain[0], "AXTitle") or ""
            _ax_log(f"PID 获取失败，尝试用 AXTitle 回退: {app_title}")

            if app_title:
                try:
                    import psutil
                    for proc in psutil.process_iter(["pid", "name"]):
                        proc_name = proc.info.get("name", "") or ""
                        base_name = proc_name.rsplit(".", 1)[0] if "." in proc_name else proc_name
                        # 宽松匹配（支持 Safari浏览器 ↔ Safari、Dock 等）
                        if (app_title.lower() in proc_name.lower() or
                            proc_name.lower() in app_title.lower() or
                            base_name.lower() in app_title.lower()):
                            app_pid = proc.info["pid"]
                            app_name = get_process_name(app_pid)
                            _ax_log(f"回退成功 → app_name={app_name} (pid={app_pid})")
                            break
                except Exception as e:
                    logger.warning(f"psutil 回退失败: {e}")

            if not app_name or app_name.lower() == "kernel_task":
                app_name = app_title or "unknown_app"

        for i, node in enumerate(chain):
            role = _ax_attr(node, "AXRole") or ""
            subrole = _ax_attr(node, "AXSubrole") or ""
            title = _ax_attr(node, "AXTitle") or ""
            value_raw = _ax_attr(node, "AXValue")
            value = str(value_raw).strip() if isinstance(value_raw, str) and value_raw.strip() else None

            index = 0
            parent_node = chain[i - 1] if i > 0 else None
            if parent_node is not None:
                siblings = _ax_attr(parent_node, "AXChildren") or []
                for j, sib in enumerate(siblings):
                    try:
                        if sib == node:
                            index = j
                            break
                    except Exception:
                        pass

            disable_keys = []
            if parent_node is not None:
                siblings = _ax_attr(parent_node, "AXChildren") or []
                same_role_count = sum(1 for s in siblings if _ax_attr(s, "AXRole") == role)
                if same_role_count <= 1:
                    disable_keys = ["cls", "value", "index"]
                    if not title:
                        disable_keys.append("name")
                else:
                    if not subrole:
                        disable_keys.append("cls")
                    if not value:
                        disable_keys.append("value")
            else:
                disable_keys = ["cls", "value", "index"]
                if not title:
                    disable_keys.append("name")

            attrs_map = {"cls": 0, "name": 0, "value": 0, "index": 0}

            path_list.append({
                "tag_name": role,
                "checked": True,
                "disable_keys": disable_keys,
                "attrs_map": attrs_map,
                "cls": subrole if subrole else "",
                "name": title,
                "value": value,
                "index": str(index),
            })

        return {
            "version": "1",
            "type": PickerDomain.UIA.value,
            "app": app_name,
            "path": path_list,
            "img": {"self": screenshot(self.rect())},
            "parent": "",
        }

    # 其余方法保持不变
    def ancestor_chain(self) -> List['AXUIElement']:
        if self.__ancestor_chain is None:
            raw_chain = _ax_ancestor_chain(self.element)
            self.__ancestor_chain = [AXUIElement(e) for e in raw_chain]
        return self.__ancestor_chain

    def attributes(self) -> Dict[str, str]:
        if self.__attributes is None:
            self.__attributes = _collect_attrs(self.element)
        return self.__attributes


# ── AXUIOperate / AXUIPicker（保持不变） ───────────────────────────────────

class AXUIOperate:
    @classmethod
    def get_cursor_pos(cls) -> tuple[int, int]:
        loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        return int(loc.x), int(loc.y)

    @classmethod
    def get_element_at(cls, point: Point) -> Optional[AXUIElement]:
        raw = _ax_get_element_at(float(point.x), float(point.y))
        if raw is None:
            return None
        return AXUIElement(raw)

    @classmethod
    def get_element_rect(cls, element: AXUIElement) -> Optional[Rect]:
        return element.rect()

    @classmethod
    def get_ancestor_chain(cls, element: AXUIElement) -> List[AXUIElement]:
        return element.ancestor_chain()

    @classmethod
    def get_element_attributes(cls, element: AXUIElement) -> Dict[str, str]:
        return element.attributes()

    @classmethod
    def get_windows_by_point(cls, point: Point) -> Optional[Any]:
        return _ax_get_element_at(float(point.x), float(point.y))

    @classmethod
    def get_process_id(cls, element: Any) -> int:
        """
        获取元素所属应用的真实 PID。

        修复前的问题：
        - 直接对叶子元素调用 _ax_get_pid，PyObjC/ctypes 混用导致 out-param
          始终为 0，映射到 kernel_task。

        修复策略（两层保险）：
        1. 主路径：_ax_get_pid 内部已向上爬到 AXApplication 再取 PID，
           并使用两种 PyObjC 调用方式依次尝试。
        2. 兜底路径：若仍得到无效结果（pid <= 1 或进程名为 kernel_task），
           改用 Quartz CGWindowListCopyWindowInfo 按鼠标当前坐标匹配
           最顶层真实应用窗口的 PID，完全绕开 AX API 的坑。
        """
        # 主路径：AX 祖先链 → AXApplication
        pid = _ax_get_pid(element)
        if pid > 1:
            proc_name = get_process_name(pid)
            if proc_name and proc_name.lower() not in ("kernel_task", ""):
                _ax_log(f"get_process_id: AX path → pid={pid} ({proc_name})")
                return pid

        # 兜底路径：Quartz 窗口列表按鼠标坐标匹配
        _ax_log(
            f"get_process_id: AX path returned invalid pid={pid}, "
            "falling back to Quartz window list"
        )
        loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        quartz_pid = _quartz_pid_at_point(loc.x, loc.y)
        if quartz_pid > 1:
            return quartz_pid

        # 实在拿不到，返回 AX 结果（即使是 0）让上层处理
        return pid

    @classmethod
    def get_app_windows(cls, element: Optional[Any]) -> Optional[Any]:
        if element is None:
            return None
        cur = element
        while cur is not None:
            if _ax_attr(cur, "AXRole") == "AXApplication":
                return cur
            parent = _ax_attr(cur, "AXParent")
            if parent is None:
                return cur
            cur = parent
        return element

    @classmethod
    def get_web_control(cls, element: Any, app: APP = None, point: Point = None) -> tuple[bool, int, int, Any]:
        try:
            chain = _ax_ancestor_chain(element)
            for i, node in enumerate(chain):
                dom_class = _ax_attr(node, "AXDOMClassList") or []
                if "View" not in dom_class:
                    continue
                if i == 0:
                    continue
                parent_node = chain[i - 1]
                parent_dom_class = _ax_attr(parent_node, "AXDOMClassList") or []
                if "BrowserView" not in parent_dom_class:
                    continue
                pv = _ax_attr(node, "AXPosition")
                pt = _ax_unpack_point(pv) if pv else None
                if pt is None:
                    continue
                menu_left, menu_top = int(pt[0]), int(pt[1])
                window_ref = _ax_attr(element, "AXWindow")
                return True, menu_top, menu_left, window_ref
        except Exception as e:
            logger.error(f"AXUIOperate.get_web_control error: {e}")
        return False, 0, 0, None


class AXUIPicker:
    @classmethod
    def get_element(cls, root: AXUIElement, point: Point, **kwargs) -> Optional[AXUIElement]:
        el = _ax_get_element_at(float(point.x), float(point.y))
        if el is None:
            return None
        return AXUIElement(element=el)


axui_picker = AXUIPicker()