import time

from astronverse.picker import PickerAction, RecordAction, SmartComponentAction


_NORMAL_PICK_ACTIONS = {a.value for a in PickerAction}
_SMART_COMPONENT_ACTIONS = {a.value for a in SmartComponentAction}
_RECORD_ACTIONS = {a.value for a in RecordAction}


class PickerServer:
    def __init__(self, service_context):
        self.service_context = service_context
        self.start_time = None  # svc.send_sign 会写入此字段

        self._normal_pick = None
        self._smart_pick = None
        self._record = None

    def _get_normal_pick(self):
        if self._normal_pick is None:
            from astronverse.picker.server.servers.normal_picker_server import NormalPickServer
            self._normal_pick = NormalPickServer(self.service_context)
        return self._normal_pick

    def _get_smart_pick(self):
        if self._smart_pick is None:
            from astronverse.picker.server.servers.smart_component_server import SmartComponentServer
            self._smart_pick = SmartComponentServer(self.service_context)
        return self._smart_pick

    def _get_record(self):
        if self._record is None:
            from astronverse.picker.server.servers.record_server import RecordServer
            self._record = RecordServer(self.service_context)
        return self._record

    def server(self):
        """公共分发循环：等待模块就绪后，按 action 路由到对应子服务"""
        while True:

            # 等待模块加载完成
            if not self.service_context.event_core:
                time.sleep(0.1)
                continue

            # 处理信号机制
            sign = self.service_context.sign()
            if any(a in sign for a in _NORMAL_PICK_ACTIONS):
                self._get_normal_pick().handle(sign)
            elif any(a in sign for a in _SMART_COMPONENT_ACTIONS):
                self._get_smart_pick().handle(sign)
            elif any(a in sign for a in _RECORD_ACTIONS):
                self._get_record().handle(sign)
            else:
                time.sleep(0.1)
