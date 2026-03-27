import asyncio

from astronverse.trigger.core.logger import logger
from pynput import keyboard


class HotKeyTask:
    def __init__(self, shortcuts: list = None, **kwargs):
        """
        构建热键监听的类

        shortcuts: `List`, 快捷键组合

        Kwargs: 该参数用于构建任务的详细参数状态
        """
        self.shortcuts = shortcuts
        self._h_handle = None  # 用于控制监听事件的对象

    async def callback(self, q: asyncio.Queue, run_event: asyncio.Event):
        async def handle_hotkey():
            logger.debug("handle_hotkey: enqueue True to asyncio.Queue")
            await q.put(True)
            try:
                logger.debug(f"handle_hotkey: queue size after put -> {q.qsize()}")
            except Exception:
                pass

        def on_hotkey_press():
            """热键触发回调"""
            try:
                is_set = run_event.is_set()
            except Exception as e:
                logger.exception(f"on_hotkey_press: failed to read run_event.is_set(): {e}")
                is_set = False
            logger.debug(f"on_hotkey_press: hotkey '{hotkey_expression}' pressed, run_event.is_set={is_set}")
            if is_set:
                logger.info("on_hotkey_press: run_event is set; ignore hotkey")
                return
            loop.call_soon_threadsafe(asyncio.create_task, handle_hotkey())
            logger.debug("on_hotkey_press: scheduled handle_hotkey on event loop")

        loop = asyncio.get_running_loop()
        hotkey_expression = "+".join(self.shortcuts)

        # 跨平台修饰键映射
        key_map = {
            "ctrl": "ctrl",
            "control": "ctrl",
            "shift": "shift",
            "alt": "alt", 
            "option": "alt",  # macOS Option = Alt
            "cmd": "cmd", 
            "command": "cmd", 
            "win": "cmd", 
            "windows": "cmd"  # macOS Cmd = Windows Win
        }

        # 转换快捷键格式：["ctrl", "shift", "f"] -> "<ctrl>+<shift>+f"
        pynput_keys = []
        for k in self.shortcuts:
            k_lower = k.lower()
            if k_lower in key_map:
                pynput_keys.append(f"<{key_map[k_lower]}>")
            else:
                pynput_keys.append(k)
        pynput_hotkey = "+".join(pynput_keys)

        logger.info(f"Registering hotkey '{hotkey_expression}' -> '{pynput_hotkey}' via pynput.keyboard.GlobalHotKeys")
        self._h_handle = keyboard.GlobalHotKeys({pynput_hotkey: on_hotkey_press})
        self._h_handle.start()

    def force_end_callback(self):
        """该方法进行热键任务回收"""
        logger.info("force_end_callback: removing hotkey listener")
        if self._h_handle:
            self._h_handle.stop()
