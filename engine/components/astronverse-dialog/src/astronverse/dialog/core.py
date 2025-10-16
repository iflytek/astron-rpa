"""
核心对话控制器相关功能模块。
"""

import json
import subprocess
import time

from pynput.mouse import Controller


class DialogController:
    """对话控制器，封装鼠标和子进程相关操作。"""

    mouse_controller = Controller()

    @staticmethod
    def get_current_mouse_position():
        """获取当前鼠标位置。"""
        current_position = DialogController.mouse_controller.position
        return current_position

    @staticmethod
    def execute_subprocess(args):
        """
        执行子进程并解析输出中的JSON数据。

        Args:
            args (list): 子进程参数列表。

        Returns:
            dict: 解析到的JSON数据（如有）。
        """
        with subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        ) as process:
            output_data = {}
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if not output:
                    continue
                output_line = output.strip()
                try:
                    output_data = json.loads(output_line)
                    print(f"output_data：{output_data}")
                except (json.JSONDecodeError, ValueError):
                    # 忽略JSON解析错误，继续处理下一行
                    pass
            try:
                time.sleep(1)
                process.kill()
            except (OSError, ProcessLookupError):
                # 进程可能已经结束，忽略错误
                pass
            return output_data

    @staticmethod
    def read_process_output(process, process_output_list):
        """
        读取子进程输出并追加到列表。

        Args:
            process: 子进程对象。
            process_output_list (list): 用于存储输出的列表。
        """
        for line in iter(process.stdout.readline, ""):
            process_output_list.append(line)
        process.stdout.close()
