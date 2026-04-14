import asyncio
import json

from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey, RequestPush, PushKey
from astronverse.picker import RecordAction
from astronverse.picker.logger import logger


class RecordHandler:

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None
        self.record_task: asyncio.Task = None

        self._continue_event: asyncio.Event = None

    async def dispatch(self, ws_server, data: dict):
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.record_action:
                case RecordAction.LISTENING:
                    await self._handle_start(request)
                case RecordAction.START:
                    await self._handle_continue(request)
                case RecordAction.PAUSE:
                    await self._send_response(ResponseKey.SUCCESS, data="已暂停")
                case RecordAction.HOVER_START:
                    await self._send_response(ResponseKey.SUCCESS, data="悬停检测已启动")
                case RecordAction.HOVER_END:
                    await self._handle_continue(request)
                case RecordAction.AUTOMIC_END:
                    await self._handle_continue(request)
                case RecordAction.END:
                    await self._handle_end(request)
        except Exception as e:
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_start(self, request: RequestMessage):
        """开始录制：启动录制循环 task"""
        if self.record_task and not self.record_task.done():
            await self._send_response(ResponseKey.SUCCESS, error="录制已在进行中")
            return
        self.record_task = asyncio.create_task(self._record_loop(request))
        await self._send_response(ResponseKey.SUCCESS, data="录制已开始")

    async def _handle_continue(self, request: RequestMessage):
        """用户挪出/确认，继续下一次拾取"""
        if self._continue_event:
            self._continue_event.set()

    async def _handle_end(self, request: RequestMessage):
        """结束录制：取消循环 task + 通知 Server 清理"""
        if self.record_task and not self.record_task.done():
            self.record_task.cancel()
            try:
                await self.record_task
            except asyncio.CancelledError:
                pass
        await self.svc.send_sign(RecordAction.END.value, {})
        await self._send_response(ResponseKey.SUCCESS, data="录制已结束")

    async def _record_loop(self, request: RequestMessage):
        """录制循环：反复拾取 → push element → 等前端 CONTINUE"""
        self._continue_event = asyncio.Event()
        while True:
            self._continue_event.clear()
            payload = request.model_dump(mode="json")
            result = await self.svc.send_sign(RecordAction.START.value, payload)
            if isinstance(result, dict):
                await self._push_element(result)
            else:
                await self._send_response(ResponseKey.ERROR, error=str(result))
            await self._continue_event.wait()

    async def _push_element(self, element: dict):
        """推送拾取到的元素给前端"""
        try:
            ws = self.ws_server.connections["record"][-1]
            await ws.send(RequestPush.create_push(
                PushKey.RECORD_ELEMENT,
                data=json.dumps(element, ensure_ascii=False),
            ).model_dump_json())
        except Exception as e:
            logger.error(f"推送元素失败: {e}")

    async def _send_response(self, key: ResponseKey, data=None, error: str = ""):
        if data is None:
            data = ""
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        ws = self.ws_server.connections["record"][-1]
        await ws.send(ResponseMessage.create_response(key, data=data, err_msg=error).model_dump_json())
