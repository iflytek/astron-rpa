# macOS implementation - based on ApplicationServices AXUIElement API
from typing import Any, Optional

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


def _ax_attr(el, attr):
    """读取 AX 属性，失败返回 None"""
    try:
        err, val = AXUIElementCopyAttributeValue(el, attr, None)
        return val if err == kAXErrorSuccess else None
    except Exception:
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


def _ax_unpack_rect(val):
    try:
        ok, rect = AS.AXValueGetValue(val, AS.kAXValueCGRectType, None)
        if ok and rect is not None:
            return rect.origin.x, rect.origin.y, rect.size.width, rect.size.height
    except Exception:
        pass
    return None


def _ax_element_rect(el) -> Optional[tuple]:
    """返回元素屏幕矩形 (x, y, w, h)，AX 坐标系（左上原点）"""
    frame_v = _ax_attr(el, "AXFrame")
    if frame_v is not None:
        rect = _ax_unpack_rect(frame_v)
        if rect and rect[2] > 0 and rect[3] > 0:
            return rect

    pv = _ax_attr(el, "AXPosition")
    sv = _ax_attr(el, "AXSize")
    if pv is None or sv is None:
        return None
    pt = _ax_unpack_point(pv)
    sz = _ax_unpack_size(sv)
    if pt and sz and sz[0] > 0 and sz[1] > 0:
        return pt[0], pt[1], sz[0], sz[1]
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


def _ax_get_element_at(x: float, y: float) -> Optional[Any]:
    """获取屏幕坐标处的 AX 元素"""
    try:
        sys_el = AXUIElementCreateSystemWide()
        err, el = AXUIElementCopyElementAtPosition(sys_el, float(x), float(y), None)
        if err == kAXErrorSuccess and el is not None:
            return el
    except Exception:
        pass
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


# ── AXUIElement（IElement 实现）──────────────────────────────────────────────


class AXUIElement(IElement):
    """macOS AXUIElement 封装，对应 Windows 的 UIAElement + MSAAElement"""

    def __init__(self, element: Any):
        self.element = element
        self.__rect: Optional[Rect] = None
        self.__tag: Optional[str] = None

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


# ── AXUIOperate（工具类）────────────────────────────────────────────────────


class AXUIOperate:
    """macOS AXUIElement 工具类，对应 Windows 的 UIAOperate"""

    @classmethod
    def get_cursor_pos(cls) -> tuple[int, int]:
        loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        return int(loc.x), int(loc.y)

    @classmethod
    def get_windows_by_point(cls, point: Point) -> Optional[Any]:
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
