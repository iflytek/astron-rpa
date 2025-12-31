import time
import traceback

from astronverse.picker import DrawResult, PickerSign, SVCSign
from astronverse.picker.core.highlight_client import highlight_client
from astronverse.picker.logger import logger


class PickerServer:
    def __init__(self, service_context):
        self.service_context = service_context
        self.start_time = None  # 用于统计是否卡顿
        self.end_time = None  # 用于统计是否卡顿

    def server(self):
        """
        处理ws_server发过来的消息，串联画框，事件监听，还有拾取核心 pick_core
        后续正常情况下无需修改该部分代码
        """
        while True:
            # 等待加载完成
            if not self.service_context.event_core:
                time.sleep(0.1)
                continue
            if not self.service_context.picker_core:
                time.sleep(0.1)
                continue

            # 外部消息处理
            sign = self.service_context.sign()
            if PickerSign.STOP.value in sign:
                try:
                    # 退出

                    # 1.隐藏画框
                    highlight_client.hide_wnd()
                    time.sleep(0.1)  # 等待画框真正隐藏

                    # 收集返回数据
                    result = None
                except Exception as e:
                    logger.error("pick error: {} {}".format(e, traceback.format_exc()))
                    result = "{}".format(e)
                finally:
                    # 2.退出事件监听
                    self.service_context.event_core.close()

                # 3.消费STOP消息,给前端
                del sign[PickerSign.STOP.value]
                result_sign = "{}_RES".format(PickerSign.STOP.value)
                sign[result_sign] = result

                logger.info("拾取结束，外部退出")
            elif PickerSign.START.value in sign:
                try:
                    # 启动事件监听
                    is_start = self.service_context.event_core.start()
                    if is_start:
                        logger.info("拾取开始")
                    event_core = self.service_context.event_core
                    if event_core.is_cancel() or event_core.is_focus():
                        # 退出

                        try:
                            # 1.隐藏画框
                            # highlight_client.hide_wnd()
                            # time.sleep(0.1)  # 等待画框真正隐藏
                            if event_core.is_cancel() or (
                                event_core.is_focus() and self.service_context.event_tag == SVCSign.PICKER
                            ):
                                highlight_client.hide_wnd()
                                time.sleep(0.1)

                            # 收集返回数据
                            if self.service_context.event_core.is_focus():
                                picker_data = sign[PickerSign.START.value]
                                result = self.service_context.picker_core.element(self.service_context, picker_data)
                            else:
                                result = "cancel"
                        except Exception as e:
                            logger.error("pick error: %s %s", e, traceback.format_exc())
                            result = "{}".format(e)
                        finally:
                            # 2.退出事件监听
                            self.service_context.event_core.close()

                        # 3.消费Cancel或者focus消息,给前端
                        del sign[PickerSign.START.value]
                        result_sign = "{}_RES".format(PickerSign.START.value)
                        sign[result_sign] = result

                        logger.info("拾取结束，主动退出")
                    else:
                        # 绘图
                        self.start_time = time.time()
                        draw_result: DrawResult = self.service_context.picker_core.draw(
                            self.service_context,
                            highlight_client,
                            sign[PickerSign.START.value],
                        )
                        self.end_time = time.time()

                        # 检查绘图结果
                        if not draw_result.success and draw_result.error_message:
                            logger.warning(f"拾取绘图失败: {draw_result.error_message}")
                            # 记录警告并继续
                            try:
                                # 1. 隐藏画框
                                highlight_client.hide_wnd()
                                time.sleep(0.1)

                                # 2. 准备异常信息
                                res = "{}".format(draw_result.error_message)
                            except Exception as cleanup_error:
                                logger.error("清理资源时出错: {}".format(cleanup_error))
                                res = "{}".format(draw_result.error_message)
                            finally:
                                # 3. 退出事件监听
                                self.service_context.event_core.close()

                            # 4. 设置响应信号，让 ws_server 能收到异常
                            del sign[PickerSign.START.value]
                            res_sign = "{}_RES".format(PickerSign.START.value)
                            sign[res_sign] = res

                            logger.info("拾取因异常结束")

                except Exception as e:
                    logger.error("pick error: {} {}".format(e, traceback.format_exc()))
            elif PickerSign.SMART_COMPONENT.value in sign:
                logger.info("智能组件上下拾取开始")
                res = self.service_context.picker_core.call_pluguin(
                    self.service_context, highlight_client, sign[PickerSign.SMART_COMPONENT.value]
                )
                del sign[PickerSign.SMART_COMPONENT.value]
                res_sign = "{}_RES".format(PickerSign.SMART_COMPONENT.value)
                sign[res_sign] = res
            else:
                # 3 休眠
                time.sleep(0.1)
