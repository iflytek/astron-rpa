from astronverse.picker.logger import logger


class RecordServer:
    """智能录制服务 - 处理录制相关信号"""

    def __init__(self, service_context):
        self.service_context = service_context

    def handle(self, sign) -> bool:
        """处理录制信号，返回是否处理了信号"""
        # todo 后续处理录制信号
        return False
