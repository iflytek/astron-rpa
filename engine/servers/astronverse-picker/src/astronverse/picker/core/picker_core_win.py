import threading
import time
from typing import Optional

from astronverse.picker import (
    DrawResult,
    IElement,
    IPickerCore,
    PickerDomain,
    PickerType,
    Point,
    Rect,
    PickerSign,
    SmartComponentAction,
)
from astronverse.picker.engines.uia_picker import UIAElement, UIAOperate
from astronverse.picker.logger import logger
from astronverse.picker.utils.browser import BrowserControlFinder
from astronverse.picker import APP


class PickerCore(IPickerCore):
    """拾取的功能集合, 比如鼠标位置，窗口，元素"""

    def __init__(self):
        self.last_point = Point(0, 0)
        self.last_element: Optional[IElement] = None
        self.last_strategy_svc = None
        self.lock = threading.Lock()

        # 保存上一次的有效绘制结果
        self.last_valid_rect: Optional[Rect] = None
        self.last_valid_tag: str = ""
        self.last_valid_domain: Optional[str] = None

    def _get_element_domain(self, element: IElement) -> str:
        """根据元素类型确定实际使用的 domain"""
        element_type = type(element).__name__
        if element_type == "UIAElement":
            return PickerDomain.UIA.value
        elif element_type == "WEBElement":
            return PickerDomain.WEB.value
        elif element_type == "MSAAElement":
            return PickerDomain.MSAA.value
        else:
            # 默认返回 UIA
            logger.warning(f"无法确定元素类型 {element_type}，使用默认 UIA domain")
            return PickerDomain.UIA.value

    def draw(self, svc, highlight_client, data: dict) -> DrawResult:
        """纯粹的拾取绘制功能，不包含录制相关逻辑"""
        try:
            # 更新鼠标位置
            p_x, p_y = UIAOperate.get_cursor_pos()
            self.last_point.x = p_x
            self.last_point.y = p_y
            pick_type = data.get("pick_type")

            if pick_type == PickerType.POINT:
                # 点拾取不需要绘制，但仍然是成功状态
                return DrawResult(success=True)

            elif pick_type == PickerType.WINDOW:
                return self._draw_window(svc, highlight_client, data)

            elif pick_type in [
                PickerType.ELEMENT,
                PickerType.SIMILAR,
                PickerType.BATCH,
            ]:
                return self._draw_element(svc, highlight_client, data)

            else:
                return DrawResult(success=False, error_message=f"不支持的拾取类型: {pick_type}")

        except Exception as e:
            logger.error(f"拾取绘制失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def _draw_window(self, svc, highlight_client, data: dict) -> DrawResult:
        """窗口拾取绘制"""
        start_control = UIAOperate.get_windows_by_point(self.last_point)
        result_control = UIAOperate.get_app_windows(start_control)
        if not result_control:
            return DrawResult(success=False, error_message="")
        with self.lock:
            self.last_element = UIAElement(control=result_control)
        process_id = UIAOperate.get_process_id(start_control)
        self.last_strategy_svc = svc.strategy.gen_svc(
            process_id=process_id,
            last_point=self.last_point,
            data=data,
            start_control=start_control,
            domain=PickerDomain.UIA,
        )
        rect = self.last_element.rect()
        tag = self.last_element.tag()
        highlight_client.draw_wnd(rect, msgs=tag)
        return DrawResult(
            success=True,
            rect=rect,
            app=self.last_strategy_svc.app.value,
            domain=PickerDomain.UIA.value,  # 窗口拾取总是使用 UIA
        )

    def _draw_element(self, svc, highlight_client, data: dict) -> DrawResult:
        """元素拾取绘制"""
        # 环境收集
        start_control = UIAOperate.get_windows_by_point(self.last_point)
        if not start_control:
            logger.info("拾取预处理 start_control 为空")
            return DrawResult(success=False, error_message="未找到起始控件")

        process_id = UIAOperate.get_process_id(start_control)

        # 上下文生成
        if not svc.strategy:
            # 等待策略加载
            timeout = 10  # 10秒超时
            wait_time = 0
            while not svc.strategy and wait_time < timeout:
                time.sleep(0.1)
                wait_time += 0.1

            if not svc.strategy:
                return DrawResult(success=False, error_message="策略加载超时（10s）")

            logger.info("strategy 加载完成")

        domain = PickerDomain.AUTO
        pick_mode = data.get("pick_mode", None)
        if pick_mode:
            if pick_mode == "WebPick":
                domain = PickerDomain.AUTO_WEB
            else:
                domain = PickerDomain.AUTO_DESK
        self.last_strategy_svc = svc.strategy.gen_svc(
            process_id=process_id, last_point=self.last_point, data=data, start_control=start_control, domain=domain
        )

        # 策略运行
        res = svc.strategy.run(self.last_strategy_svc)
        if not res:
            return DrawResult(success=False, error_message="")

        with self.lock:
            self.last_element = res
        current_rect = self.last_element.rect()
        current_tag = self.last_element.tag()

        # 确定实际使用的 domain
        actual_domain = self._get_element_domain(self.last_element)

        # 更新缓存
        self.last_valid_rect = current_rect
        self.last_valid_tag = current_tag
        self.last_valid_domain = actual_domain

        # 绘制
        highlight_client.draw_wnd(current_rect, msgs=current_tag)

        return DrawResult(
            success=True,
            rect=current_rect,
            app=self.last_strategy_svc.app.value,
            domain=actual_domain,
        )

    def call_pluguin(self, svc, high_light, data: dict):
        """为单独向插件通信定制"""
        import json, time

        pick_type = data.get("pick_type", "")
        pick_sign = data.get("pick_sign", "")
        smart_component_action = data.get("smart_component_action", "")
        # time.sleep(5)
        p_x, p_y = UIAOperate.get_cursor_pos()
        cur_point = Point(0, 0)
        cur_point.x = p_x
        cur_point.y = p_y
        # start_control = UIAOperate.get_windows_by_point(cur_point)
        data_str = data.get("data", "{}")
        data_dict = json.loads(data_str) if isinstance(data_str, str) else data_str
        data["data"] = data_dict
        # 然后从解析后的字典中获取值
        app = data_dict.get("app")
        title = data_dict.get("path", {}).get("tabTitle", "")
        parent_control = BrowserControlFinder.get_control_by_app_name(app, title)
        start_control = BrowserControlFinder.get_document_control(parent_control)
        if not start_control:
            logger.info("拾取预处理 start_control 为空")
            return "未找到浏览器，请重试"

        process_id = UIAOperate.get_process_id(start_control)
        if pick_type in [PickerType.ELEMENT]:
            if pick_sign == PickerSign.SMART_COMPONENT:
                # 上下文生成
                if not svc.strategy:
                    # 等待策略加载
                    timeout = 10  # 10秒超时
                    wait_time = 0
                    while not svc.strategy and wait_time < timeout:
                        time.sleep(0.1)
                        wait_time += 0.1

                    if not svc.strategy:
                        return "策略加载超时（10s）"

                    logger.info("strategy 加载完成")

                cur_strategy_svc = svc.strategy.gen_svc(
                    process_id=process_id,
                    last_point=cur_point,
                    data=data,
                    start_control=start_control,
                    domain=PickerDomain.WEB,
                )

                # 策略运行
                try:
                    res = svc.strategy.run(cur_strategy_svc)
                    if res:
                        cur_rect = res.rect()
                        cur_tag = res.tag()
                        if smart_component_action in [SmartComponentAction.PREVIOUS, SmartComponentAction.NEXT]:
                            high_light.draw_wnd(cur_rect, msgs=cur_tag)
                        return res.path(svc, cur_strategy_svc)
                except Exception as e:
                    logger.info(f"智能组件出现异常 {e}")
                    res = str(e)
                return res

    def element(self, svc, data: dict) -> dict:
        pick_type = data.get("pick_type")
        if pick_type == PickerType.POINT:
            point_data = {"x": self.last_point.x, "y": self.last_point.y}
            return {"point": point_data, "version": "1"}
        elif pick_type == PickerType.WINDOW or pick_type in [PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]:
            with self.lock:
                if self.last_element:
                    return self.last_element.path(svc, self.last_strategy_svc)
                return {}
        else:
            raise NotImplementedError()
