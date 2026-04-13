import json

from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey
from astronverse.picker import RecordAction
from astronverse.picker.utils.utils import call


class RecordHandler:

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None

    async def dispatch(self, ws_server, data: dict):
        """处理录制消息，统一捕获异常并回复错误"""
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.record_action:
                case RecordAction.LISTENING:
                    await self._handle_listening(request)
                case RecordAction.START:
                    await self._handle_start(request)
                case RecordAction.PAUSE:
                    await self._handle_pause(request)
                case RecordAction.HOVER_START:
                    await self._handle_hover_start(request)
                case RecordAction.HOVER_END:
                    await self._handle_hover_end(request)
                case RecordAction.AUTOMIC_END:
                    await self._handle_atomic_end(request)
                case RecordAction.END:
                    await self._handle_end(request)
        except Exception as e:
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_listening(self, request: RequestMessage):
        """开始监听 - 通知 picker_server 进入监听状态"""
        # todo 后续处理
        pass

    async def _handle_start(self, request: RequestMessage):
        """开始录制 - 通知 picker_server 开始录制"""
        # todo 后续处理
        pass

    async def _handle_pause(self, request: RequestMessage):
        """暂停录制 - 通知 picker_server 暂停录制"""
        # todo 后续处理
        pass

    async def _handle_hover_start(self, request: RequestMessage):
        """开始选择原子能力 - 通知 picker_server 进入原子能力悬停选择"""
        # todo 后续处理
        pass

    async def _handle_hover_end(self, request: RequestMessage):
        """放弃选择原子能力 - 通知 picker_server 取消原子能力悬停"""
        # todo 后续处理
        pass

    async def _handle_atomic_end(self, request: RequestMessage):
        """原子能力选择完成 - 通知 picker_server 原子能力操作结束"""
        # todo 后续处理
        pass

    async def _handle_end(self, request: RequestMessage):
        """结束录制 - 通知 picker_server 结束录制，隐藏遮罩层"""
        # todo 后续处理
        pass

    async def _send_response(self, key: ResponseKey, data="", error: str = ""):
        if data is None:
            data = ""
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        ws = self.ws_server.connections["record"][-1]
        await ws.send(ResponseMessage.create_response(key, data=data if key == ResponseKey.SUCCESS else "", err_msg=error).model_dump_json())

