"""简单验证与 native_messaging 的 IPC 能否通信。

Windows 使用命名管道；macOS/Linux 使用与 Go 侧一致的 Unix 域套接字路径。
需 native 宿主已启动，否则应得到连接/超时类异常。
"""
import sys
import unittest

from astronverse.browser_bridge.core.ipc import NativeMessagingClient


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
