import json

from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey
from astronverse.picker import SmartComponentAction, PickerSign, SVCSign
from astronverse.picker.utils.utils import call


class SmartComponentHandler:

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None

    async def dispatch(self, ws_server, data: dict):
        """处理智能组件消息，统一捕获异常并回复错误"""
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.smart_component_action:
                case SmartComponentAction.START:
                    # todo 后续处理
                    pass
                case SmartComponentAction.NEXT:
                    # todo 后续处理
                    pass
                case SmartComponentAction.PREVIOUS:
                    # todo 后续处理
                    pass
                case SmartComponentAction.CANCEL:
                    await self._handle_cancel(request)
                case SmartComponentAction.END:
                    await self._handle_end(request)
        except Exception as e:
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_cancel(self, request: RequestMessage):
        """取消拾取 - 隐藏遮罩层"""
        # todo 后续处理
        await self._send_response(ResponseKey.SUCCESS)

    async def _handle_end(self, request: RequestMessage):
        """完成拾取 - 隐藏遮罩层"""
        # todo 后续处理
        await self._send_response(ResponseKey.SUCCESS)

    async def _send_response(self, key: ResponseKey, data="", error: str = "未知错误"):
        ws = self.ws_server.connections["smart_component"][-1]
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        await ws.send(ResponseMessage.create_response(
            key,
            data=data if key == ResponseKey.SUCCESS else "",
            err_msg=error,
        ).model_dump_json())
