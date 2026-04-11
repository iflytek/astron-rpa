import asyncio
import json
from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey
from astronverse.picker import PickerAction
from astronverse.picker.utils.utils import call


class PickerHandler:

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None

    async def dispatch(self, ws_server, data: dict):
        """处理消息，统一捕获异常并回复错误"""
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.pick_action:
                case PickerAction.START:
                    pass
                case PickerAction.STOP:
                    pass
                case PickerAction.VALIDATE:
                    await self._handle_validate(request)
                case PickerAction.GAIN:
                    await self._handle_gain(request)
                case PickerAction.HIGHLIGHT:
                    await self._handle_highlight(request)
        except Exception as e:
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_validate(self, request: RequestMessage):
        """处理拾取校验"""
        def _locate_rects():
            from astronverse.locator.locator import LocatorManager
            data = self._process_element_data(request)
            res = LocatorManager().locator(data)
            return [item.rect() for item in res] if isinstance(res, list) else res.rect()

        try:
            await self.ws_server.hl.start("validate")
            rects = await call(_locate_rects)
            await self.ws_server.hl.draw(rects, "", "validate")
            await asyncio.sleep(3)
            await self._send_response(ResponseKey.SUCCESS, data="校验成功")
        finally:
            await self.ws_server.hl.hide()

    async def _handle_gain(self, request: RequestMessage):
        """处理拾取获取数据"""
        def _fetch_data():
            from astronverse.locator.locator import LocatorManager
            from astronverse.picker.utils.browser import Browser
            from astronverse.picker.utils.table_filter import DataFilter, table_json_merge_values

            data = self._process_element_data(request)
            data = LocatorManager.parse_element_json(data) if isinstance(data, str) else data
            web_info = Browser.send_browser_extension(
                browser_type=data.get("app"),
                data=data.get("path"),
                key="getBatchData",
                gate_way_port=self.svc.route_port,
            )
            values = web_info["values"]
            batch_element = table_json_merge_values(data.get("path"), values)
            return DataFilter(data_json=batch_element).get_filtered_data()

        locate_data = await call(_fetch_data)
        await self._send_response(ResponseKey.SUCCESS, data=locate_data)

    async def _handle_highlight(self, request: RequestMessage):
        """处理拾取高亮"""
        def _do_highlight():
            from astronverse.locator.locator import LocatorManager
            from astronverse.picker.utils.browser import Browser

            data = self._process_element_data(request)
            data = LocatorManager.parse_element_json(data) if isinstance(data, str) else data
            Browser.send_browser_extension(
                browser_type=data.get("app"),
                data=data.get("path"),
                key="highLightColumn",
                gate_way_port=self.svc.route_port,
            )

        await call(_do_highlight)
        await self._send_response(ResponseKey.SUCCESS, data="高亮成功")

    @staticmethod
    def _process_element_data(request: RequestMessage):
        """处理元素数据"""
        from astronverse.locator.locator import LocatorManager
        from astronverse.picker.utils.params import complex_param_parser

        global_data = (request.ext_data or {}).get("global", [])
        data = (LocatorManager.parse_element_json(request.data) if isinstance(request.data, str) else request.data)
        return complex_param_parser(complex_param=data, global_data=global_data)

    async def _send_response(self, key: ResponseKey, data="", error: str = "未知错误"):
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        ws = self.ws_server.connections["picker"][-1]
        await ws.send(ResponseMessage.create_response(key, data=data, err_msg=error).model_dump_json())
