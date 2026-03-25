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


# ── AX 工具函数（来自验证代码）──────────────────────────────────────────────

AX_DEBUG = True

def _ax_log(msg: str):
    if AX_DEBUG:
        logger.info(f"[AX] {msg}")





def _ax_attr(el, attr):
    """读取 AX 属性，失败返回 None"""
    try:
        err, val = AXUIElementCopyAttributeValue(el, attr, None)
        return val if err == kAXErrorSuccess else None
    except Exception:
        return None


def _ax_attr_names(el) -> List[str]:
    """获取元素所有属性名"""
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
    """将 AX 元素的位置信息转换为 Rect(left, top, right, bottom)"""
    r = _ax_element_rect(el)
    if r is None:
        return None
    x, y, w, h = r
    return Rect(int(x), int(y), int(x + w), int(y + h))


def _ax_get_pid(el) -> int:
    try:
        import ctypes

        pid = ctypes.c_int(0)
        AXUIElementGetPid(el, ctypes.byref(pid))
        return pid.value
    except Exception:
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
            _ax_log(f"{indent} child[{i}] no rect")
            continue

        if not contains(child_rect):
            _ax_log(f"{indent} child[{i}] miss")
            continue

        _ax_log(f"{indent} child[{i}] HIT {child_rect}")

        sub = _ax_find_deepest_at_point(child, x, y, depth + 1, max_depth)
        sub_rect = _ax_element_rect(sub)

        if sub_rect:
            area = sub_rect[2] * sub_rect[3]
            if area < best_area:
                _ax_log(f"{indent} -> better area={area}")
                best = sub
                best_area = area

    return best


def _ax_get_element_at(x: float, y: float) -> Optional[Any]:
    try:
        _ax_log(f"\n=== HIT TEST ({x},{y}) ===")

        sys_el = AXUIElementCreateSystemWide()
        err, el = AXUIElementCopyElementAtPosition(sys_el, float(x), float(y), None)

        if err == kAXErrorSuccess and el is not None:
            _ax_log("initial element OK")

            refined = _ax_find_deepest_at_point(el, x, y)

            role = _ax_attr(refined, "AXRole")
            title = _ax_attr(refined, "AXTitle") or _ax_attr(refined, "AXLabel")

            _ax_log(f"FINAL => role={role}, title={title}")

            return refined

        _ax_log(f"hit failed err={err}")

    except Exception as e:
        logger.exception(f"_ax_get_element_at error: {e}")

    return None


def _ax_ancestor_chain(el) -> list:
    """从当前元素向上收集祖先链（顺序：顶层 → 当前元素）"""
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


# ── 属性收集与格式化（移植自代码1）─────────────────────────────────────────


def _format_ax_value(attr: str, val) -> str:
    """格式化 AX 属性值，用于展示"""
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
    """收集元素所有属性，返回格式化后的字典，与代码1行为一致"""
    PRIORITY = [
        "AXRole", "AXRoleDescription", "AXTitle", "AXLabel",
        "AXValue", "AXDescription", "AXHelp", "AXEnabled",
        "AXFocused", "AXSelected", "AXExpanded", "AXIdentifier",
        "AXPosition", "AXSize",
    ]
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


# ── AXUIElement（IElement 实现）──────────────────────────────────────────────


class AXUIElement(IElement):
    """macOS AXUIElement 封装，对应 Windows 的 UIAElement + MSAAElement"""

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
        """构建元素路径 dict，供 locator 定位使用。

        路径格式与 Windows UIAElement.path() 兼容：
          tag_name → AXRole
          cls      → AXSubrole
          name     → AXTitle
          value    → AXValue（仅字符串）
          index    → 在父节点 AXChildren 中的位置
        """
        chain = _ax_ancestor_chain(self.element)
        path_list = []

        for i, node in enumerate(chain):
            role = _ax_attr(node, "AXRole") or ""
            subrole = _ax_attr(node, "AXSubrole") or ""
            title = _ax_attr(node, "AXTitle") or ""
            value_raw = _ax_attr(node, "AXValue")
            value = str(value_raw).strip() if isinstance(value_raw, str) and value_raw.strip() else None

            # 计算 index（在父节点 AXChildren 中的位置）
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

            # 计算 disable_keys
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

            path_list.append(
                {
                    "tag_name": role,
                    "cls": subrole if subrole else None,
                    "name": title,
                    "value": value,
                    "index": index,
                    "checked": True,
                    "disable_keys": disable_keys,
                }
            )

        pid = _ax_get_pid(self.element)
        app_name = get_process_name(pid)

        return {
            "version": "1",
            "type": PickerDomain.UIA.value,
            "app": app_name,
            "path": path_list,
            "img": {"self": screenshot(self.rect())},
        }

    def ancestor_chain(self) -> List['AXUIElement']:
        """返回祖先链（从顶层到当前元素）的 AXUIElement 列表"""
        if self.__ancestor_chain is None:
            raw_chain = _ax_ancestor_chain(self.element)
            self.__ancestor_chain = [AXUIElement(e) for e in raw_chain]
        return self.__ancestor_chain

    def attributes(self) -> Dict[str, str]:
        """返回元素所有属性的格式化字典（与代码1一致）"""
        if self.__attributes is None:
            self.__attributes = _collect_attrs(self.element)
        return self.__attributes


# ── AXUIOperate（工具类）────────────────────────────────────────────────────


class AXUIOperate:
    """macOS AXUIElement 工具类，对应 Windows 的 UIAOperate"""

    @classmethod
    def get_cursor_pos(cls) -> tuple[int, int]:
        loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        return int(loc.x), int(loc.y)

    @classmethod
    def get_element_at(cls, point: Point) -> Optional[AXUIElement]:
        """根据屏幕坐标获取 AXUIElement 对象"""
        raw = _ax_get_element_at(float(point.x), float(point.y), highlight)
        if raw is None:
            return None
        return AXUIElement(raw)

    @classmethod
    def get_element_rect(cls, element: AXUIElement) -> Optional[Rect]:
        """获取元素的屏幕矩形"""
        return element.rect()

    @classmethod
    def get_ancestor_chain(cls, element: AXUIElement) -> List[AXUIElement]:
        """获取元素的祖先链（顶层 → 当前）"""
        return element.ancestor_chain()

    @classmethod
    def get_element_attributes(cls, element: AXUIElement) -> Dict[str, str]:
        """获取元素的所有属性"""
        return element.attributes()

    @classmethod
    def get_windows_by_point(cls, point: Point) -> Optional[Any]:
        """原始方法，返回原生 AXUIElement 对象（兼容旧接口）"""
        return _ax_get_element_at(float(point.x), float(point.y))

    @classmethod
    def get_process_id(cls, element: Any) -> int:
        return _ax_get_pid(element)

    @classmethod
    def get_app_windows(cls, element: Optional[Any]) -> Optional[Any]:
        """向上遍历 AXParent，找到 AXRole == AXApplication 的节点"""
        if element is None:
            return None
        cur = element
        while cur is not None:
            role = _ax_attr(cur, "AXRole")
            if role == "AXApplication":
                return cur
            parent = _ax_attr(cur, "AXParent")
            if parent is None:
                return cur
            cur = parent
        return element

    @classmethod
    def get_web_control(
        cls,
        element: Any,
        app: APP = None,
        point: Point = None,
    ) -> tuple[bool, int, int, Any]:
        """判断当前元素是否在浏览器的 web 内容区域内。

        macOS 判断逻辑（来自提示内容）：
        命中节点的祖先链中，存在节点 A 满足：
          - A 的 AXDOMClassList 包含 "View"
          - A 的直接父节点 B 的 AXDOMClassList 包含 "BrowserView"
        若存在这样的 A，则 is_document=True，
        menu_left/menu_top 从节点 A 的 AXPosition 获取。

        返回: (is_document, menu_top, menu_left, window_ref)
        """
        try:
            chain = _ax_ancestor_chain(element)
            for i, node in enumerate(chain):
                dom_class = _ax_attr(node, "AXDOMClassList") or []
                if "View" not in dom_class:
                    continue
                # 检查直接父节点是否有 BrowserView
                if i == 0:
                    continue
                parent_node = chain[i - 1]
                parent_dom_class = _ax_attr(parent_node, "AXDOMClassList") or []
                if "BrowserView" not in parent_dom_class:
                    continue
                # 命中：从节点 A 的 AXPosition 获取坐标
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


# ── AXUIPicker（拾取器）─────────────────────────────────────────────────────


class AXUIPicker:
    """macOS AXUIElement 拾取器，对应 Windows 的 UIAPicker + MSAAPicker"""

    @classmethod
    def get_element(cls, root: AXUIElement, point: Point, **kwargs) -> Optional[AXUIElement]:
        """从 root 开始，找到包含 point 的面积最小的叶子元素。

        直接用 AXUIElementCopyElementAtPosition 获取最精确的命中元素，
        与 Windows UIAPicker 的行为一致。
        """
        el = _ax_get_element_at(float(point.x), float(point.y))
        if el is None:
            return None
        return AXUIElement(element=el)


axui_picker = AXUIPicker()