import json

from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey
from astronverse.picker import PickerType, SmartComponentAction


class SmartComponentHandler:

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None

    async def dispatch(self, ws_server, data: dict):
        """处理智能组件消息（结构与 NormalPickerHandler.dispatch 一致：match 分支 + 专用 _handle_*）"""
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.smart_component_action:
                case SmartComponentAction.START:
                    await self._handle_start(request)
                case SmartComponentAction.NEXT | SmartComponentAction.PREVIOUS:
                    await self._handle_navigate(request)
                case SmartComponentAction.CANCEL | SmartComponentAction.END:
                    await self._handle_stop(request)
        except Exception as e:
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_start(self, request: RequestMessage):
        """开始拾取：高亮 + send_sign(SMART_COMPONENT_START)"""
        try:
            await self.ws_server.hl.start("normal")
            payload = self._build_start_sign_payload(request)
            result = await self.svc.send_sign(request.smart_component_action.value, payload)
            if result == "cancel":
                await self._send_response(ResponseKey.CANCEL, error="")
            elif isinstance(result, dict):
                out = dict(result)
                out["picker_type"] = request.pick_type.name
                await self._send_response(ResponseKey.SUCCESS, data=out)
            else:
                await self._send_response(ResponseKey.ERROR, error=str(result))
        finally:
            await self.ws_server.hl.hide()

    async def _handle_navigate(self, request: RequestMessage):
        """上下级切换：直接 send_sign，由 picker 侧负责重绘高亮"""
        try:
            payload = self._build_start_sign_payload(request)
            result = await self.svc.send_sign(request.smart_component_action.value, payload)
            if result == "cancel":
                await self._send_response(ResponseKey.CANCEL, error="")
            elif isinstance(result, dict):
                out = dict(result)
                out["picker_type"] = request.pick_type.name
                await self._send_response(ResponseKey.SUCCESS, data=out)
            else:
                await self._send_response(ResponseKey.ERROR, error=str(result))
        finally:
            pass

    async def _handle_stop(self, request: RequestMessage):
        """取消 / 结束拾取：隐藏高亮 + send_sign（与 NormalPickerHandler._handle_stop 形态一致）"""
        await self.svc.send_sign(request.smart_component_action.value, request.model_dump(mode="json"))
        await self._send_response(ResponseKey.SUCCESS)

    def _build_start_sign_payload(self, request: RequestMessage) -> dict:
        """与 ws_server.back 中拾取开始一致：SIMILAR/BATCH 需先解析元素与 pick_mode"""
        request.data = self._process_element_data(request)

        # 特殊处理 pick_mode
        if request.pick_mode and isinstance(request.data, dict):
            request.data["pick_mode"] = request.pick_mode.value

        return request.model_dump(mode="json")

    @staticmethod
    def _process_element_data(request: RequestMessage):
        """处理元素数据"""
        if not request.data:
            return None

        from astronverse.locator.locator import LocatorManager
        from astronverse.picker.utils.params import complex_param_parser

        global_data = (request.ext_data or {}).get("global", [])
        data = (LocatorManager.parse_element_json(request.data) if isinstance(request.data, str) else request.data)
        return complex_param_parser(complex_param=data, global_data=global_data)

    async def _send_response(self, key: ResponseKey, data=None, error: str = ""):
        if data is None:
            data = ""
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        ws = self.ws_server.connections["smart_component"][-1]
        await ws.send(ResponseMessage.create_response(key, data=data, err_msg=error).model_dump_json())
