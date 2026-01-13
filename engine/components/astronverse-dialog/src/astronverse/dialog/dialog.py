import json
import threading
import time
import urllib.parse
from typing import Callable, Optional

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.dialog import *


def wait_with_timeout(check_done: Callable[[], bool], reset_timeout_on_activity: bool, wait_time: int):
    """
    等待对话框结果，支持用户活动检测和超时保护

    Args:
        check_done: 回调函数，返回 True 表示完成，False 表示继续等待
        reset_timeout_on_activity: 是否在检测到用户活动（鼠标移动）时重置超时计时器
        wait_time: 超时时间（秒）
    """
    from pynput.mouse import Controller as MouseController

    mouse_controller: Optional[MouseController] = None
    if reset_timeout_on_activity:
        mouse_controller = MouseController()

    last_pos = None
    start = time.time()
    while not check_done():
        if reset_timeout_on_activity and mouse_controller:
            pos = mouse_controller.position
            if pos != last_pos:
                last_pos = pos
                start = time.time()
        if time.time() - start > wait_time:
            break
        time.sleep(0.1)


class Dialog:
    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("message_type", formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value)),
            atomicMg.param(
                "message_content",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                limitLength=[-1, 120],
            ),
            atomicMg.param("button_type"),
            atomicMg.param(
                "auto_check",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                dynamics=[DynamicsItem(key="$this.wait_time.show", expression="return $this.auto_check.value == true")],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "default_button_c",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_c.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.CONFIRM.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_cn",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_cn.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.CONFIRM_CANCEL.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_y",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_y.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.YES_NO.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_yn",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_yn.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.YES_NO_CANCEL.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "preview_button", formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value), required=False
            ),
        ],
        outputList=[atomicMg.param("result_button", types="Str")],
    )
    def message_box(
        box_title: str = "消息提示框",
        message_type: MessageType = MessageType.MESSAGE,
        message_content: str = "",
        button_type: ButtonType = ButtonType.CONFIRM,
        auto_check: bool = False,
        wait_time: int = 60,
        default_button_c: DefaultButtonC = DefaultButtonC.CONFIRM,
        default_button_cn: DefaultButtonCN = DefaultButtonCN.CONFIRM,
        default_button_y: DefaultButtonY = DefaultButtonY.YES,
        default_button_yn: DefaultButtonYN = DefaultButtonYN.YES,
        preview_button=None,
        **kwargs,
    ):
        if wait_time is None:
            wait_time = 60 if auto_check else 620

        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        payload = {
            "key": "Dialog.message_box",
            "box_title": box_title,
            "message_type": message_type.value,
            "message_content": message_content,
            "button_type": button_type.value,
            "auto_check": auto_check,
            "wait_time": wait_time,
            "outputkey": "result_button",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        wait_with_timeout(lambda: done.is_set(), reset_timeout_on_activity=auto_check, wait_time=wait_time)
        if res_e:
            raise Exception(res_e)

        if not res and auto_check:
            default_mapping = {
                ButtonType.CONFIRM: default_button_c.value,
                ButtonType.CONFIRM_CANCEL: default_button_cn.value,
                ButtonType.YES_NO: default_button_y.value,
                ButtonType.YES_NO_CANCEL: default_button_yn.value,
            }
            return default_mapping[button_type]
        return res.get("result_button", None)

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("input_type"),
            atomicMg.param("input_title", types="Str", required=False, limitLength=[-1, 60]),
            atomicMg.param(
                "default_input_text",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.default_input_text.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param(
                "default_input_pwd",
                formType=AtomicFormTypeMeta(type=AtomicFormType.DEFAULTPASSWORD.value),
                required=False,
                limitLength=[4, 16],
                dynamics=[
                    DynamicsItem(
                        key="$this.default_input_pwd.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.PASSWORD.value),
                    )
                ],
            ),
            atomicMg.param(
                "preview_button", formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value), required=False
            ),
        ],
        outputList=[atomicMg.param("input_content", types="Str")],
    )
    def input_box(
        box_title: str = "输入对话框",
        input_type: InputType = InputType.TEXT,
        input_title: str = "输入框标题",
        default_input_text: str = "",
        default_input_pwd: str = "",
        preview_button=None,
    ):
        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        if input_type == InputType.TEXT:
            default_input = default_input_text
        elif input_type == InputType.PASSWORD:
            default_input = default_input_pwd
        else:
            raise NotImplementedError()
        payload = {
            "key": "Dialog.input_box",
            "box_title": box_title,
            "input_type": input_type.value,
            "input_title": input_title,
            "default_input": default_input,
            "outputkey": "input_content",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        done.wait()
        if res_e:
            raise Exception(res_e)

        return res.get("input_content", None)

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("select_type"),
            atomicMg.param("options", formType=AtomicFormTypeMeta(AtomicFormType.OPTIONSLIST.value), need_parse="str"),
            atomicMg.param(
                "options_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
            ),
            atomicMg.param(
                "preview_button", formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value), required=False
            ),
        ],
        outputList=[atomicMg.param("select_result", types="Any")],
    )
    def select_box(
        box_title: str = "选择对话框",
        select_type: SelectType = SelectType.SINGLE,
        options: list = [],
        options_title: str = "",
        preview_button=None,
    ):
        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        payload = {
            "key": "Dialog.select_box",
            "box_title": box_title,
            "select_type": select_type.value,
            "options": options,
            "options_title": options_title,
            "outputkey": "select_result",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        done.wait()
        if res_e:
            raise Exception(res_e)

        return res.get("select_result", None)

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("time_type", required=False),
            atomicMg.param("time_format", required=False),
            atomicMg.param(
                "default_time",
                required=False,
                formType=AtomicFormTypeMeta(AtomicFormType.DEFAULTDATEPICKER.value, params={"format": "YYYY-MM-DD"}),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_time.show",
                        expression="return $this.time_type.value == '{}'".format(TimeType.TIME.value),
                    ),
                    DynamicsItem(
                        key="$this.default_time.formType.params.format", expression="return $this.time_format.value"
                    ),
                ],
            ),
            atomicMg.param(
                "default_time_range",
                required=False,
                formType=AtomicFormTypeMeta(AtomicFormType.RANGEDATEPICKER.value, params={"format": "YYYY-MM-DD"}),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_time_range.show",
                        expression="return $this.time_type.value == '{}'".format(TimeType.TIME_RANGE.value),
                    ),
                    DynamicsItem(
                        key="$this.default_time.formType.params.format", expression="return $this.time_format.value"
                    ),
                ],
            ),
            atomicMg.param(
                "input_title", formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value), required=False, types="Str"
            ),
            atomicMg.param(
                "preview_button", formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value), required=False
            ),
        ],
        outputList=[atomicMg.param("select_time", types="Any")],
    )
    def select_time_box(
        box_title: str = "日期时间选择框",
        time_type: TimeType = TimeType.TIME,
        time_format: TimeFormat = TimeFormat.YEAR_MONTH_DAY,
        default_time: str = "",
        default_time_range: list = ["", ""],
        input_title: str = "输入框标题",
        preview_button: bool = None,
    ):
        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        payload = {
            "key": "Dialog.select_time_box",
            "box_title": box_title,
            "time_type": time_type.value,
            "time_format": time_format.value,
            "default_time": default_time,
            "default_time_range": default_time_range,
            "input_title": input_title,
            "outputkey": "select_time",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        done.wait()
        if res_e:
            raise Exception(res_e)

        return res.get("select_time") if (res.get("select_time") and res.get("select_time") != ["", ""]) else None

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title_file",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.box_title_file.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
                limitLength=[-1, 50],
            ),
            atomicMg.param(
                "box_title_folder",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.box_title_folder.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FOLDER.value),
                    )
                ],
                limitLength=[-1, 50],
            ),
            atomicMg.param("open_type", required=False),
            atomicMg.param(
                "file_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_type.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "multiple_choice",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.multiple_choice.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "select_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 60],
            ),
            atomicMg.param(
                "default_path",
                required=False,
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value, params={"filters": [], "file_type": "folder"}
                ),
            ),
            atomicMg.param(
                "preview_button", formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value), required=False
            ),
        ],
        outputList=[atomicMg.param("select_file", types="Any")],
    )
    def select_file_box(
        box_title_file: str = "文件选择框",
        box_title_folder="文件夹选择框",
        open_type: OpenType = OpenType.FILE,
        file_type: FileType = FileType.ALL,
        multiple_choice: bool = True,
        select_title: str = "",
        default_path: str = "",
        preview_button=None,
    ):
        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        if open_type == OpenType.FILE:
            box_title = box_title_file
        elif open_type == OpenType.FOLDER:
            box_title = box_title_folder
        else:
            raise NotImplementedError()
        payload = {
            "key": "Dialog.select_file_box",
            "box_title": box_title,
            "open_type": open_type.value,
            "file_type": file_type.value,
            "multiple_choice": multiple_choice,
            "select_title": select_title,
            "default_path": default_path,
            "outputkey": "select_file",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        done.wait()
        if res_e:
            raise Exception(res_e)
        return res.get("select_file", None)

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                limitLength=[-1, 50],
            ),
            atomicMg.param(
                "design_interface",
                types="Str",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
                need_parse="json_str",
            ),
            atomicMg.param(
                "auto_check",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                dynamics=[DynamicsItem(key="$this.wait_time.show", expression="return $this.auto_check.value == true")],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "default_button",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button.show",
                        expression="return $this.auto_check.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("dialog_result", types="DialogResult")],
    )
    def custom_box(
        box_title: str = "自定义对话框",
        design_interface: dict = None,
        auto_check: bool = False,
        wait_time: int = 60,
        default_button: DefaultButtonCN = DefaultButtonCN.CONFIRM,
    ) -> dict:
        if wait_time is None:
            wait_time = 60 if auto_check else 620

        done = threading.Event()
        res = {}
        res_e = None

        def callback_func(watch_msg, e: Exception = None):
            nonlocal done, res, res_e
            if watch_msg:
                res = watch_msg.data
            if e:
                res_e = e
            done.set()

        payload = {
            "key": "Dialog.custom_box",
            "box_title": box_title,
            "design_interface": json.dumps(design_interface.get("value"), ensure_ascii=False),
            "result_button": default_button.value,
            "outputkey": "dialog_result",
        }
        ws = atomicMg.cfg().get("WS", None)
        if ws:
            ws.send_reply({"data": {"name": "userform", "option": payload}}, 600, callback_func)

        wait_with_timeout(lambda: done.is_set(), auto_check, wait_time)
        if res_e:
            raise Exception(res_e)

        if not res and auto_check:
            if design_interface.get("value").get("table_required"):
                res["result_button"] = DefaultButtonCN.CANCEL.value
            else:
                res["result_button"] = DefaultButtonCN.CONFIRM.value
        return res
