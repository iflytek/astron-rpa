import asyncio
import json
import sys
from websockets import ServerConnection
import websockets
from astronverse.picker import PickerType
from astronverse.picker.logger import logger
from astronverse.picker.server import ResponseMessage, ResponseKey


class WsServer:
    """WebSocket服务器 - 连接管理 + pick_sign 路由"""

    loop = None

    def __init__(self, svc, port: int):
        self.svc = svc
        self.port = port
        self.connections: dict[str, list[ServerConnection]] = {
            "_unidentified": [],
            "picker": [],
            "record": [],
            "hl": [],
            "smart_component": [],
        }
        self._picker_handler = None
        self._hl_handler = None
        self._record_handler = None
        self._smart_component_handler = None

    def _add(self, ws: ServerConnection) -> None:
        """新连接放入未识别池"""
        self.connections["_unidentified"].append(ws)

    def _move(self, ws: ServerConnection, target: str) -> None:
        """将连接从当前所在 bucket 移入目标 bucket"""
        for conns in self.connections.values():
            if ws in conns:
                conns.remove(ws)
                break
        self.connections[target].append(ws)

    def _remove(self, ws: ServerConnection) -> None:
        """从所有 bucket 中移除连接"""
        for conns in self.connections.values():
            if ws in conns:
                conns.remove(ws)
                break

    def _import_picker_handler(self):
        if self._picker_handler is None:
            from astronverse.picker.server.handlers.normal_picker_handler import NormalPickerHandler
            self._picker_handler = NormalPickerHandler(self.svc)
        return self._picker_handler

    def _import_hl_handler(self):
        if self._hl_handler is None:
            from astronverse.picker.server.handlers.hl_handler import HlHandler
            self._hl_handler = HlHandler(self.connections)
        return self._hl_handler

    def _import_record_handler(self):
        if self._record_handler is None:
            from astronverse.picker.server.handlers.record_handler import RecordHandler
            self._record_handler = RecordHandler(self.svc)
        return self._record_handler

    def _import_smart_component_handler(self):
        if self._smart_component_handler is None:
            from astronverse.picker.server.handlers.smart_component_handler import SmartComponentHandler
            self._smart_component_handler = SmartComponentHandler(self.svc)
        return self._smart_component_handler

    @property
    def hl(self):
        return self._import_hl_handler()

    async def websocket_endpoint(self, ws: ServerConnection):
        # 业务通道确认
        path = ws.request.path
        if path in ["", "/"]:
            # 业务通道，业务通道需要读取他的第一个消息来确定
            self._add(ws)
        elif path == "/?tag=hl":
            # 高亮通道
            self._add(ws)
            self._move(ws, "hl")

        # 消息分发
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                    if data.get("message_type") == "ack":
                        # 推送消息
                        continue
                    if data.get("pick_type", None):
                        # 拾取消息
                        pick_type = data.get("pick_type", None)
                        if pick_type == PickerType.RECORD.value:
                            self._move(ws, "record")
                            await self._import_record_handler().dispatch(ws_server=self, data=data)
                        elif pick_type == PickerType.SMART_COMPONENT.value:
                            self._move(ws, "smart_component")
                            await self._import_smart_component_handler().dispatch(ws_server=self, data=data)
                        else:
                            self._move(ws, "picker")
                            await self._import_picker_handler().dispatch(ws_server=self, data=data)
                            pass
                except Exception as e:
                    try:
                        import traceback
                        logger.error("WebSocket消息处理错误: {} stack: {}".format(e, traceback.format_exc()))
                        await ws.send(ResponseMessage.create_response(ResponseKey.ERROR, err_msg=str(e)).model_dump_json())
                    except Exception:
                        pass
        finally:
            self._remove(ws)

    def server(self):
        if sys.platform == "win32":
            import pythoncom
            try:
                pythoncom.CoInitialize()  # noqa
            except Exception as e:
                pass

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        WsServer.loop = loop

        async def _start():
            srv = await websockets.serve(self.websocket_endpoint, "127.0.0.1", self.svc.conf.port)
            logger.info("服务已启动 ws://127.0.0.1:%s", self.svc.conf.port)
            await asyncio.Event().wait()  # 永远挂起，等价于 run_forever
            return srv

        loop.run_until_complete(_start())  # 这里循环就转起来了
