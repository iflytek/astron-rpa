import json
import subprocess
import time

from pynput.mouse import Controller


class DialogCore:
    mouse = Controller()

    @staticmethod
    def get_mouse_position():
        current_position = DialogCore.mouse.position
        return current_position

    @staticmethod
    def exe_run(args):
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        save_dict = {}

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if not output:
                continue
            save_str = output.strip()
            try:
                save_dict = json.loads(save_str)
                print(f"save_dict：{save_dict}")
            except Exception as error:
                pass
        try:
            time.sleep(1)
            process.kill()
        except Exception:
            pass

        return save_dict

    @staticmethod
    def read_output(process, output_list):
        for line in iter(process.stdout.readline, ""):
            output_list.append(line)
        process.stdout.close()
