import os
import sys

import pyautogui
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import WinPick
from astronverse.actionlib.utils import FileExistenceType, handle_existence, Credential
from astronverse.input.code.keyboard import Keyboard
from astronverse.locator import PickerDomain, Point
from astronverse.winelement import (
    ElementInputType,
    MouseClickButton,
    MouseClickKeyboard,
    MouseClickType,
)
from astronverse.winelement.core import IWinEleCore
from astronverse.winelement.error import *

if sys.platform == "win32":
    from astronverse.winelement.core_win import WinEleCore
elif sys.platform == "darwin":
    from astronverse.winelement.core_mac import WinEleCore
else:
    from astronverse.winelement.core_win import WinEleCore

WinEleCore: IWinEleCore = WinEleCore()


def _modifier_key_name(keyboard_input: MouseClickKeyboard) -> str:
    if sys.platform == "darwin" and keyboard_input == MouseClickKeyboard.WIN:
        return "command"
    return keyboard_input.value


def _clear_text_field(locator, clear_first: bool):
    if not clear_first:
        Keyboard.press("end")
        return

    if sys.platform == "win32":
        import uiautomation

        window_control = locator.control()
        if window_control.ControlTypeName == uiautomation.EditControl.ControlTypeName:
            window_control.GetValuePattern().SetValue("")
            return

        Keyboard.press("home")
        Keyboard.hotkey("ctrl", "a")
        Keyboard.press("delete")
        return

    Keyboard.hotkey("command", "a")
    Keyboard.press("backspace")


class WinEle:
    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
    )
    def click_element(
        pick: WinPick,
        click_button: MouseClickButton = MouseClickButton.LEFT,
        click_type: MouseClickType = MouseClickType.CLICK,
        wait_time: float = 10.0,
        horizontals_offset: int = 0,
        verticals_offset: int = 0,
        keyboard_input: MouseClickKeyboard = MouseClickKeyboard.NONE,
    ):
        locator = WinEleCore.find(pick, wait_time)
        point = locator.point()

        # 按下辅助按键
        if keyboard_input != MouseClickKeyboard.NONE:
            Keyboard.key_down(_modifier_key_name(keyboard_input))
        try:
            locator.move(Point(point.x + int(horizontals_offset), point.y + int(verticals_offset)))
            pyautogui.click(
                clicks=1 if click_type == MouseClickType.CLICK else 2,
                button=click_button.value,
            )
        except Exception as e:
            raise e
        finally:
            # 记得释放
            if keyboard_input != MouseClickKeyboard.NONE:
                Keyboard.key_up(_modifier_key_name(keyboard_input))

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
    )
    def screenshot_element(
        pick: WinPick,
        file_path: str,
        file_name: str = "桌面元素截图",
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        if not file_name.endswith(".png"):
            file_name += ".png"

        new_file_path = handle_existence(os.path.join(file_path, file_name), exist_type)
        if not new_file_path:
            raise BizException(PATH_ERROR, "拾取或保存路径有误")

        locator = WinEleCore.find(pick=pick)
        window_rect = locator.rect()
        rect = (
            window_rect.left,
            window_rect.top,
            window_rect.width(),
            window_rect.height(),
        )
        screenshot = pyautogui.screenshot(region=rect)
        screenshot.save(new_file_path)

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
    )
    def hover_element(pick: WinPick, wait_time: float = 10.0):
        locator = WinEleCore.find(pick, wait_time)
        locator.hover()

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
            atomicMg.param(
                "text",
                dynamics=[
                    DynamicsItem(
                        key="$this.text.show",
                        expression="return $this.input_type.value == '{}'".format(ElementInputType.KEYBOARD.value),
                    )
                ],
            ),
            atomicMg.param(
                "credential_text",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": ["credential"]}),
                dynamics=[
                    DynamicsItem(
                        key="$this.credential_text.show",
                        expression=f"return $this.input_type.value == '{ElementInputType.Credential.value}'",
                    )
                ],
            ),
        ],
    )
    def input_text_element(
        pick: WinPick,
        input_type: ElementInputType = ElementInputType.KEYBOARD,
        text: str = "",
        credential_text: str = "",
        clear_first: bool = True,
        wait_time: float = 10.0,
    ):
        if pick.get("elementData", {}).get("type", None) != PickerDomain.UIA.value:
            raise BizException(
                UNPICKABLE_FORMAT.format(pick.get("type", None)), "类型不支持{}".format(pick.get("type", None))
            )

        locator = WinEleCore.find(pick, wait_time)
        locator.move()
        pyautogui.click()
        _clear_text_field(locator, clear_first)

        if input_type == ElementInputType.KEYBOARD:
            Keyboard.write_unicode(text)
        elif input_type == ElementInputType.CLIPBOARD:
            Keyboard.paste_hotkey()
        elif input_type == ElementInputType.Credential:
            if not credential_text:
                raise BizException(CREDENTIAL_NOT_SELECTED, "请先选择凭据名称")
            Keyboard.write_unicode(Credential.get_credential(credential_text))

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
        outputList=[atomicMg.param("ele_text", types="Str")],
    )
    def get_element_text(pick: WinPick, wait_time: float = 10.0):
        locator = WinEleCore.find(pick, wait_time)
        return locator.control().Name

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        outputList=[
            atomicMg.param("get_similar_ele", types="List"),
        ],
    )
    def similar(pick: WinPick, wait_time: int = 10) -> list:
        if pick.get("elementData", {}).get("type", None) != PickerDomain.UIA.value:
            raise BizException(
                UNPICKABLE_FORMAT.format(pick.get("type", None)), "类型不支持{}".format(pick.get("type", None))
            )

        locator_list = WinEleCore.find(pick, wait_time)
        res_list = []
        if locator_list:
            if not isinstance(locator_list, list):
                locator_list = [locator_list]
            for locator in locator_list:
                win_pick = WinPick()
                win_pick.locator = locator
                res_list.append(win_pick)
        return res_list
