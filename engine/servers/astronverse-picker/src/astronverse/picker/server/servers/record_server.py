import threading
import time
from typing import Optional

from astronverse.picker import (
    DrawResult,
    IElement,
    PickerDomain,
    Point,
    RecordAction,
    Rect,
    RECORDING_BLACKLIST,
)
from astronverse.picker.engines.uia_picker import UIAOperate
from astronverse.picker.logger import logger
from astronverse.picker.server.servers.normal_picker_server import _get_element_domain
from astronverse.picker.utils.process import find_real_application_process


class RecordServer:
    """录制服务 - 对齐 NormalPickServer 结构，单次拾取逻辑 + HoverCore 悬停检测"""

    def __init__(self, service_context):
        # 核心服务组件
        self.service_context = service_context
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

        # 黑名单开关
        self.enable_blacklist = True

    def handle(self, sign):
        """处理录制信号（类比 NormalPickServer.handle）"""
        if RecordAction.END.value in sign:
            # 停止绘框：删除 START 信号，让 send_sign(START) 返回
            if RecordAction.START.value in sign:
                del sign[RecordAction.START.value]
                sign[f"{RecordAction.START.value}_RES"] = None

            result = self.element(self.service_context, {})

            del sign[RecordAction.END.value]
            sign[f"{RecordAction.END.value}_RES"] = result
            logger.info("录制结束，返回元素数据")
        elif RecordAction.START.value in sign:
            # 持续绘框：只有出错才写 START_RES
            draw_result: DrawResult = self.draw(
                self.service_context,
                sign[RecordAction.START.value],
            )
            if not draw_result.success and draw_result.error_message:
                result = "{}".format(draw_result.error_message)

                del sign[RecordAction.START.value]
                sign[f"{RecordAction.START.value}_RES"] = result
                logger.info("录制拾取因异常结束")

    def draw(self, svc, data: dict) -> DrawResult:
        """执行一次拾取绘框"""
        try:
            p_x, p_y = UIAOperate.get_cursor_pos()
            self.last_point.x = p_x
            self.last_point.y = p_y

            start_control = UIAOperate.get_windows_by_point(self.last_point)
            if not start_control:
                logger.info("拾取预处理 start_control 为空")
                return DrawResult(success=False, error_message="未找到起始控件")

            process_id = UIAOperate.get_process_id(start_control)

            # 黑名单检查：若当前进程在黑名单中，复用上次缓存结果
            if self.enable_blacklist:
                process_info = find_real_application_process(process_id)
                process_name = process_info["name"]
                if process_name in RECORDING_BLACKLIST:
                    return DrawResult(
                        success=True,
                        rect=self.last_valid_rect,
                        app=process_name,
                        domain=self.last_valid_domain,
                    )

            # 等待strategy加载
            timeout = 10
            wait_time = 0
            while not svc.strategy and wait_time < timeout:
                time.sleep(0.1)
                wait_time += 0.1
            if not svc.strategy:
                return DrawResult(success=False, error_message="策略加载超时（10s）")
            logger.info("strategy 加载完成")

            self.last_strategy_svc = svc.strategy.gen_svc(
                process_id=process_id,
                last_point=self.last_point,
                data=data,
                start_control=start_control,
                domain=PickerDomain.AUTO,
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
            logger.error(f"拾取绘框失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def element(self, svc, data: dict = None) -> Optional[dict]:
        """获取当前拾取元素的路径数据"""
        with self.lock:
            if self.last_element:
                return self.last_element.path(svc, self.last_strategy_svc)
            return {}
