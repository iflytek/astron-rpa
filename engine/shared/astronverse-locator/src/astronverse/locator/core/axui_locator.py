# macOS implementation - AXUIElement based locator
# Replaces both uia_locator.py and msaa_locator.py on macOS.
import ctypes
from copy import deepcopy
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


def _window_like_title(el) -> str:
    return (
        _ax_attr(el, "AXTitle")
        or _ax_attr(el, "AXLabel")
        or _ax_attr(el, "AXDescription")
        or ""
    )


def _is_window_like_element(el) -> bool:
    role = _ax_attr(el, "AXRole") or ""
    subrole = _ax_attr(el, "AXSubrole") or ""
    if role in {"AXWindow", "AXSheet", "AXDialog"}:
        return True
    return subrole in {
        "AXStandardWindow",
        "AXDialog",
        "AXSystemDialog",
        "AXFloatingWindow",
    }


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
        if picker_type == PickerType.SIMILAR.value:
            return cls.__find_similar__(ele)
        return cls.__find_one__(ele, picker_type)

    @classmethod
    def __find_one__(cls, ele: dict, picker_type: str) -> Union[AXUILocator, None]:
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
                    logger.info("PickerType.WINDOW，查找真实窗口节点")
                    window_element = cls._find_window(root, path_list[0])
                    if window_element is not None:
                        return AXUILocator(window_element)
                    logger.debug(f"PID {pid} 未找到匹配窗口，继续下一个 PID")
                    continue

                search_list = [(root, "1")]
                element_found, search_list = cls._walk_path(search_list, path_list[1:], start_level=1)

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
    def _find_window(cls, root, node_dict: dict):
        from astronverse.locator.utils.match import MatchType, match_value

        attrs_map = node_dict.get("attrs_map") or {}
        disable_keys = set(node_dict.get("disable_keys", []))
        expected_tag = node_dict.get("tag_name") if "tag_name" not in disable_keys else None
        expected_cls = node_dict.get("cls") if "cls" not in disable_keys else None
        expected_name = node_dict.get("name") if "name" not in disable_keys else None

        windows = _ax_attr(root, "AXWindows") or []
        focused_window = _ax_attr(root, "AXFocusedWindow")
        main_window = _ax_attr(root, "AXMainWindow")

        ordered_windows = []
        for window in [focused_window, main_window, *windows]:
            if window is None or window in ordered_windows:
                continue
            ordered_windows.append(window)

        logger.debug(
            f"_find_window: expected tag={expected_tag}, cls={expected_cls}, "
            f"name={expected_name}, windows={len(ordered_windows)}"
        )

        for window in ordered_windows:
            role = _ax_attr(window, "AXRole") or ""
            subrole = _ax_attr(window, "AXSubrole") or ""
            title = _window_like_title(window)
            normalized_role = str(role).replace("AX", "") if role else ""

            if not _is_window_like_element(window):
                continue
            if expected_tag is not None and not match_value(
                expected_tag,
                normalized_role,
                attrs_map.get("tag_name", MatchType.EXACT),
            ):
                continue
            if expected_cls is not None and not match_value(
                expected_cls,
                subrole,
                attrs_map.get("cls", MatchType.EXACT),
            ):
                continue
            if expected_name not in (None, "") and not match_value(
                expected_name,
                title,
                attrs_map.get("name", MatchType.EXACT),
            ):
                continue

            logger.info(f"_find_window: 命中窗口 role={role}, subrole={subrole}, title={title}")
            return window

        return None

    @classmethod
    def __find_similar__(cls, ele: dict) -> list[AXUILocator]:
        """
        相似元素查找：遍历父容器的所有子元素，返回结构相似的元素列表。

        路径约定：
        - 带 similar_parent=True 的节点用于导航到父容器（由 picker 层标记）。
        - 不带该标记的节点用于匹配相似子元素（name/index 已由 picker 层放入 disable_keys）。
        - 若 picker 层尚未设置 similar_parent（兼容旧数据），则自动将末尾节点视为
          相似匹配层，并强制忽略 name/value/index 以找到所有同类兄弟元素。
        """
        from ApplicationServices import AXUIElementCreateApplication

        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return []

        parent_path = [v for v in path_list if v.get("similar_parent", False)]
        child_nodes = [v for v in path_list if not v.get("similar_parent", False)]

        # 兼容旧数据：picker 未设置 similar_parent 时，末尾节点作为相似层，强制忽略 name/value/index
        if not parent_path:
            parent_path = path_list[:-1] if len(path_list) > 1 else path_list
            if path_list:
                last_node = deepcopy(path_list[-1])
                forced_disable = set(last_node.get("disable_keys", [])) | {"name", "value", "index"}
                last_node["disable_keys"] = list(forced_disable)
                child_nodes = [last_node]
            else:
                child_nodes = []

        logger.debug(f"__find_similar__: parent_path 层数={len(parent_path)}, child_nodes 层数={len(child_nodes)}")

        # 导航到父容器
        pids = cls._find_pids_by_name(app_name)
        if not pids:
            raise BizException(NO_FIND_ELEMENT, f"找不到应用: {app_name}")

        parent_el = None
        for pid in pids:
            try:
                root = AXUIElementCreateApplication(pid)
                if root is None:
                    continue

                search_list = [(root, "1")]
                ok, search_list = cls._walk_path(search_list, parent_path[1:], start_level=1)

                if ok and search_list:
                    search_list.sort(key=lambda x: -int(x[1]))
                    parent_el = search_list[0][0]
                    break
            except Exception as e:
                logger.error(f"__find_similar__: PID {pid} 导航父路径异常: {e}", exc_info=True)
                continue

        if parent_el is None:
            raise BizException(NO_FIND_ELEMENT, "相似元素：父容器无法找到")

        # 遍历父容器所有直接子元素，逐一与 child_nodes 匹配
        res: list[AXUILocator] = []
        children = _ax_attr(parent_el, "AXChildren") or []
        logger.debug(f"__find_similar__: 父容器有 {len(children)} 个子元素，开始相似匹配")

        for child in children:
            if not child_nodes:
                res.append(AXUILocator(child))
                continue

            first_mp = cls._extract_match_params(child_nodes[0])
            if not cls._match_child(
                child,
                first_mp["tag_name"],
                first_mp["cls_name"],
                first_mp["name"],
                first_mp["value"],
                first_mp["attrs_map"],
            ):
                continue

            if len(child_nodes) == 1:
                res.append(AXUILocator(child))
            else:
                sub_list = [(child, "1")]
                found, sub_list = cls._walk_path(sub_list, child_nodes[1:], start_level=1)

                if found and sub_list:
                    sub_list.sort(key=lambda x: -int(x[1]))
                    res.append(AXUILocator(sub_list[0][0]))

        logger.info(f"__find_similar__: 共找到 {len(res)} 个相似元素")
        return res

    @classmethod
    def _walk_path(cls, search_list, path_nodes: list, start_level: int = 1):
        current_level = start_level
        node_idx = 0

        while node_idx < len(path_nodes):
            node_dict = path_nodes[node_idx]
            if not node_dict.get("checked", True):
                node_idx += 1
                continue

            match_params = cls._extract_match_params(node_dict)
            logger.debug(
                f"第 {current_level} 层 → tag={match_params['tag_name']},"
                f" cls={match_params['cls_name']}, name={match_params['name']},"
                f" value={match_params['value']}, index={match_params['expected_idx']}"
            )

            next_list = cls._collect_matches(search_list, match_params)
            if not next_list:
                next_checked = cls._next_checked_node(path_nodes, node_idx + 1)
                if cls._is_skippable_container(node_dict) and next_checked is not None:
                    skip_idx, skip_node = next_checked
                    skip_params = cls._extract_match_params(skip_node)
                    logger.debug(
                        f"第 {current_level} 层未命中，尝试跳过不稳定容器 {node_dict.get('tag_name')}，"
                        f"直接匹配下一层 tag={skip_params['tag_name']}"
                    )
                    skipped_list = cls._collect_matches(search_list, skip_params)
                    if skipped_list:
                        logger.warning(
                            f"第 {current_level} 层容器 {node_dict.get('tag_name')} 已跳过，使用下一层继续匹配"
                        )
                        search_list = skipped_list
                        current_level += 2
                        node_idx = skip_idx + 1
                        continue

                logger.warning(f"✗ 第 {current_level} 层匹配失败！没有找到任何符合条件的子元素")
                return False, search_list

            search_list = next_list
            current_level += 1
            node_idx += 1

        return True, search_list

    @classmethod
    def _next_checked_node(cls, path_nodes: list, start_idx: int):
        for idx in range(start_idx, len(path_nodes)):
            node = path_nodes[idx]
            if node.get("checked", True):
                return idx, node
        return None

    @classmethod
    def _is_skippable_container(cls, node_dict: dict) -> bool:
        tag_name = node_dict.get("tag_name") or ""
        if tag_name not in {"AXGroup", "AXScrollArea"}:
            return False
        disable_keys = set(node_dict.get("disable_keys", []))
        return "name" in disable_keys and "value" in disable_keys

    @classmethod
    def _extract_match_params(cls, node_dict: dict) -> dict:
        disable_keys = node_dict.get("disable_keys", [])
        expected_idx = node_dict.get("index") if "index" not in disable_keys else None
        if expected_idx in (None, ""):
            expected_idx = None
        else:
            try:
                expected_idx = int(expected_idx)
            except Exception:
                expected_idx = None
        return {
            "tag_name": node_dict.get("tag_name") if "tag_name" not in disable_keys else None,
            "cls_name": node_dict.get("cls") if "cls" not in disable_keys else None,
            "name": node_dict.get("name") if "name" not in disable_keys else None,
            "value": node_dict.get("value") if "value" not in disable_keys else None,
            "expected_idx": expected_idx,
            "attrs_map": node_dict.get("attrs_map"),
        }

    @classmethod
    def _collect_matches(cls, search_list, match_params: dict) -> list:
        next_list = []
        for parent_el, parent_sort in search_list:
            children = _ax_attr(parent_el, "AXChildren") or []
            logger.debug(f"  父节点有 {len(children)} 个子元素")
            for child_idx, child in enumerate(children):
                if cls._match_child(
                    child,
                    match_params["tag_name"],
                    match_params["cls_name"],
                    match_params["name"],
                    match_params["value"],
                    match_params["attrs_map"],
                ):
                    index_ok = match_params["expected_idx"] is None or child_idx == match_params["expected_idx"]
                    sort_str = parent_sort + ("1" if index_ok else "0")
                    next_list.append((child, sort_str))
                    logger.debug(f"    ✓ 命中子元素 idx={child_idx} sort={sort_str}")
        return next_list

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