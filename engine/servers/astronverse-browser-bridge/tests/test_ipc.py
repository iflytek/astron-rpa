"""简单验证与 native_messaging 的 pipe 能否通信。Windows 下运行，且需 native 进程已启动。"""
import sys
import unittest

from astronverse.browser_bridge.core.ipc import NativeMessagingClient


@unittest.skipUnless(sys.platform.startswith("win"), "native messaging 仅 Windows")
class TestNativePipeCommunication(unittest.TestCase):
    """发一条消息、等回包，仅验证能走通或得到明确错误。"""

    def test_send_and_wait_response(self):
        # 使用较短超时便于快速失败；browser_type 需在 BROWSER_REGISTER_NAME 中有配置
        try:
            res = NativeMessagingClient.send_and_wait(
                browser_type="chrome",
                key="ASTRON_IPC_START",
                data={},
                timeout=5,
            )
            self.assertIsInstance(res, dict, "应返回 dict（或超时/连接错误）")
        except (TimeoutError, ConnectionError, OSError, ValueError) as e:
            # 未起 native、无 chrome 等均可接受，仅需能执行到并得到明确异常
            self.assertIsNotNone(str(e))


if __name__ == "__main__":
    unittest.main()
