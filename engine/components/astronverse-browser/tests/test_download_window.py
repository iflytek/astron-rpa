import sys
from types import ModuleType

from astronverse.browser.core import core_win


def test_download_window_waits_for_filename_with_multiple_dots(monkeypatch):
    origin_name = "report.v1.pdf"
    expected_path = "/downloads/report.v1.pdf"

    win32con = ModuleType("win32con")
    win32con.WM_GETTEXTLENGTH = 1
    win32con.WM_GETTEXT = 2
    win32con.WM_COMMAND = 3

    win32gui = ModuleType("win32gui")
    win32gui.FindWindow = lambda *_args: 1
    win32gui.FindWindowEx = lambda *_args: 2
    win32gui.PyMakeBuffer = bytearray
    win32gui.PyGetBufferAddressAndLen = lambda buffer: (buffer, len(buffer))
    win32gui.PyGetString = lambda _buffer, _length: origin_name

    def send_message(_hwnd, message, *_args):
        if message == win32con.WM_GETTEXTLENGTH:
            return len(origin_name)
        return 0

    win32gui.SendMessage = send_message

    pyperclip = ModuleType("pyperclip")
    pyperclip.copy = lambda _value: None
    pyautogui = ModuleType("pyautogui")
    pyautogui.hotkey = lambda *_args: None

    monkeypatch.setitem(sys.modules, "win32con", win32con)
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)
    monkeypatch.setitem(sys.modules, "pyperclip", pyperclip)
    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui)
    monkeypatch.setattr(core_win.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(core_win.os.path, "exists", lambda path: path == expected_path)

    result = core_win.BrowserCore.download_window_operate(
        browser_type="chrome",
        is_wait=True,
        time_out=3,
        file_name="",
        custom_flag=False,
        save_path="/downloads",
    )

    assert result == expected_path
