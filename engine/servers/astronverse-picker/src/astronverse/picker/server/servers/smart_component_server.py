import threading
import time
from typing import Optional
import json

from astronverse.picker import (
    DrawResult,
    IElement,
    PickerDomain,
    PickerType,
    Point,
    Rect,
    SmartComponentAction,
)
from astronverse.picker.engines.uia_picker import UIAOperate
from astronverse.picker.logger import logger
from astronverse.picker.server.servers.normal_picker_server import _get_element_domain
from astronverse.picker.utils.browser import BrowserControlFinder


class SmartComponentServer:
    """
    智能组件拾取服务 — 结构与 NormalPickServer 对齐：event_core、hl、缓存元素与策略上下文。

    仅支持 pick_type == ELEMENT（策略层仍通过 pick_sign=SMART_COMPONENT 走 web 智能组件分支）。
    首次拾取使用信号键 SMART_COMPONENT_START；上下级使用 SMART_COMPONENT_NEXT / SMART_COMPONENT_PREVIOUS。

    与普通拾取通道隔离后，focus / ESC 退出时均隐藏高亮。
    """

    def __init__(self, service_context):
        # 核心服务组件
        self.service_context = service_context
        self.event_core = service_context.event_core
        self.hl = service_context.ws_server.hl

        # lock 保护 last_element 的读写
        self.lock = threading.Lock()

        # 缓存上一个拾取信息并对后续处理
        self.last_point = Point(0, 0)
        self.last_element: Optional[IElement] = None
        self.last_strategy_svc = None
        self.last_valid_rect: Optional[Rect] = None
        self.last_valid_tag: str = ""
        self.last_valid_domain: Optional[str] = None

    def handle(self, sign):
        """处理智能组件拾取信号"""
        if SmartComponentAction.CANCEL.value in sign or SmartComponentAction.END.value in sign:
            if SmartComponentAction.CANCEL.value in sign:
                stop_key = SmartComponentAction.CANCEL.value
            else:
                stop_key = SmartComponentAction.END.value
            self.hl.hide_sync()
            self.event_core.close()

            result = None

            del sign[stop_key]
            sign["{}_RES".format(stop_key)] = result
            logger.info("智能组件拾取结束，外部退出")
        elif SmartComponentAction.START.value in sign:
            is_start = self.event_core.start()
            if is_start:
                logger.info("智能组件拾取开始")
            is_focus = self.event_core.is_focus()
            is_cancel = self.event_core.is_cancel()
            if is_focus or is_cancel:
                # self.hl.hide_sync() # 拾取不会主动退出隐藏高亮
                self.event_core.close()

                result = "cancel"

                if is_focus:
                    try:
                        picker_data = sign[SmartComponentAction.START.value]
                        result = self.element(self.service_context, picker_data)
                    except Exception as e:
                        result = "{}".format(e)

                del sign[SmartComponentAction.START.value]
                sign["{}_RES".format(SmartComponentAction.START.value)] = result
                logger.info("拾取结束，主动退出")
            else:
                draw_result: DrawResult = self.draw(
                    self.service_context,
                    sign[SmartComponentAction.START.value],
                )
                if not draw_result.success and draw_result.error_message:

                    self.hl.hide_sync()
                    self.event_core.close()

                    result = "{}".format(draw_result.error_message)

                    del sign[SmartComponentAction.START.value]
                    sign["{}_RES".format(SmartComponentAction.START.value)] = result
                    logger.info("拾取因异常结束")
        elif SmartComponentAction.NEXT.value in sign or SmartComponentAction.PREVIOUS.value in sign:
            if SmartComponentAction.NEXT.value in sign:
                action_key = SmartComponentAction.NEXT.value
            else:
                action_key = SmartComponentAction.PREVIOUS.value

            try:
                result = self.navigate(self.service_context, sign[action_key])
            except Exception as e:
                result = "{}".format(e)

            del sign[action_key]
            sign["{}_RES".format(action_key)] = result
            logger.info(f"智能组件上下级")

    def draw(self, svc, data: dict) -> DrawResult:
        try:
            p_x, p_y = UIAOperate.get_cursor_pos()
            self.last_point.x = p_x
            self.last_point.y = p_y

            start_control = UIAOperate.get_windows_by_point(self.last_point)
            if not start_control:
                logger.info("拾取预处理 start_control 为空")
                return DrawResult(success=False, error_message="未找到起始控件")

            process_id = UIAOperate.get_process_id(start_control)

            if not svc.strategy:
                timeout = 10
                wait_time = 0
                while not svc.strategy and wait_time < timeout:
                    time.sleep(0.1)
                    wait_time += 0.1
                if not svc.strategy:
                    return DrawResult(success=False, error_message="策略加载超时（10s）")
                logger.info("strategy 加载完成")

            domain = PickerDomain.AUTO
            pick_mode = data.get("pick_mode")
            if pick_mode:
                domain = PickerDomain.AUTO_WEB if pick_mode == "WebPick" else PickerDomain.AUTO_DESK

            self.last_strategy_svc = svc.strategy.gen_svc(
                process_id=process_id,
                last_point=self.last_point,
                data=data,
                start_control=start_control,
                domain=domain,
            )

            res = svc.strategy.run(self.last_strategy_svc)
            if not res:
                return DrawResult(success=False, error_message="")

            with self.lock:
                self.last_element = res
            current_rect = self.last_element.rect()
            current_tag = self.last_element.tag()
            actual_domain = _get_element_domain(self.last_element)

            self.last_valid_rect = current_rect
            self.last_valid_tag = current_tag
            self.last_valid_domain = actual_domain

            self.hl.draw_sync(current_rect, msgs=current_tag)
            return DrawResult(
                success=True,
                rect=current_rect,
                app=self.last_strategy_svc.app.value,
                domain=actual_domain,
            )
        except Exception as e:
            logger.error(f"拾取绘制失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def element(self, svc, data: dict) -> dict:
        pick_type = data.get("pick_type")
        if pick_type == PickerType.SMART_COMPONENT:
            with self.lock:
                if self.last_element:
                    return self.last_element.path(svc, self.last_strategy_svc)
                return {}
        else:
            raise NotImplementedError()

    def navigate(self, svc, data: dict) -> dict:
        try:
            # 整理data
            payload = data.get("data", {})
            payload = json.loads(payload) if isinstance(payload, str) else payload
            data["data"] = payload

            p_x, p_y = UIAOperate.get_cursor_pos()
            pick_type = data.get("pick_type")
            if pick_type != PickerType.SMART_COMPONENT:
                return {}

            # 获取
            app = payload.get("app")
            title = payload.get("path", {}).get("tabTitle", "")
            parent_control = BrowserControlFinder.get_control_by_app_name(app, title)
            start_control = BrowserControlFinder.get_document_control(parent_control)
            if not start_control:
                logger.error(f"start_control error: empty")
                return {}
            process_id = UIAOperate.get_process_id(start_control)

            if not svc.strategy:
                timeout = 10
                wait_time = 0
                while not svc.strategy and wait_time < timeout:
                    time.sleep(0.1)
                    wait_time += 0.1
                if not svc.strategy:
                    logger.error(f"策略加载超时（10s）")
                logger.info("strategy 加载完成")

            strategy_svc = svc.strategy.gen_svc(
                process_id=process_id,
                last_point=Point(p_x, p_y),
                data=data,
                start_control=start_control,
                domain=PickerDomain.WEB,
            )
            element = svc.strategy.run(self.last_strategy_svc)
            if not element:
                return {}

            # 结果渲染
            current_rect = element.rect()
            current_tag = element.tag()
            self.hl.draw_sync(current_rect, msgs=current_tag)

            # 返回path
            return element.path(svc, strategy_svc)
        except Exception as e:
            logger.error(f"拾取navigate绘制失败: {e}")
            return {}
