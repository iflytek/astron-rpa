import json
import subprocess
import time
from pynput.mouse import Controller


class DialogController:
    mouse_controller = Controller()

    @staticmethod
    def get_current_mouse_position():
        current_position = DialogController.mouse_controller.position
        return current_position

    @staticmethod
    def execute_subprocess(args):
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
        for line in iter(process.stdout.readline, ""):
            process_output_list.append(line)
        process.stdout.close()
