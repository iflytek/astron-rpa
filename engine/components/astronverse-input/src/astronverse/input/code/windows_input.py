"""
Windows Unicode 输入方案
解决了代理对、输入验证、错误处理等问题
"""

import ctypes
import time
from ctypes import wintypes
from typing import Union

# Windows API 常量定义
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# 虚拟键码映射（用于特殊键）
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E


# 定义 Windows 结构体
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    )


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    )


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD))


class _INPUTunion(ctypes.Union):
    _fields_ = (("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT))


class INPUT(ctypes.Structure):
    _fields_ = (("type", wintypes.DWORD), ("union", _INPUTunion))


# 加载 user32.dll
user32 = ctypes.WinDLL("user32", use_last_error=True)


class InputError(Exception):
    """输入错误异常"""

    pass


class UnicodeInput:
    """Windows Unicode 输入类 - 改进版"""

    def __init__(self, delay=0.01, max_retries=1):
        """
        初始化输入器

        Args:
            delay: 每个字符输入后的延迟时间（秒），默认0.01秒
            max_retries: 发送失败时的最大重试次数
        """
        self.delay = delay
        self.max_retries = max_retries

    def _send_unicode_char(self, char):
        """
        发送单个 Unicode 字符（支持代理对）

        Args:
            char: 要发送的字符
        """
        # 将字符转换为UTF-16LE编码
        try:
            utf16_bytes = char.encode("utf-16-le")
        except Exception as e:
            raise InputError(f"字符编码失败: {char}, 错误: {e}")

        # UTF-16LE 每2个字节代表一个编码单元
        # 对于基本多文种平面(BMP)的字符，只有一个编码单元
        # 对于补充平面的字符（如emoji），有两个编码单元（代理对）
        all_inputs = []

        for i in range(0, len(utf16_bytes), 2):
            code_unit = int.from_bytes(utf16_bytes[i : i + 2], "little")

            # 按下事件
            input_down = INPUT()
            input_down.type = INPUT_KEYBOARD
            input_down.union.ki.wVk = 0
            input_down.union.ki.wScan = code_unit
            input_down.union.ki.dwFlags = KEYEVENTF_UNICODE
            input_down.union.ki.time = 0
            input_down.union.ki.dwExtraInfo = None
            all_inputs.append(input_down)

            # 释放事件
            input_up = INPUT()
            input_up.type = INPUT_KEYBOARD
            input_up.union.ki.wVk = 0
            input_up.union.ki.wScan = code_unit
            input_up.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            input_up.union.ki.time = 0
            input_up.union.ki.dwExtraInfo = None
            all_inputs.append(input_up)

        # 发送输入（带重试机制）
        for attempt in range(self.max_retries):
            try:
                array_type = INPUT * len(all_inputs)
                input_array = array_type(*all_inputs)
                result = user32.SendInput(len(all_inputs), input_array, ctypes.sizeof(INPUT))

                if result == len(all_inputs):
                    return  # 成功

                # 部分成功或失败
                error_code = ctypes.get_last_error()
                if attempt < self.max_retries - 1:
                    time.sleep(0.01)  # 短暂延迟后重试
                    continue
                else:
                    raise InputError(
                        f"SendInput 失败: 期望发送 {len(all_inputs)} 个输入，"
                        f"实际发送 {result} 个, 错误代码: {error_code}"
                    )
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(0.01)
                    continue
                else:
                    raise InputError(f"发送字符 '{char}' 失败: {e}")

    def _send_special_key(self, vk_code):
        """
        发送特殊键（如回车、退格等）

        Args:
            vk_code: 虚拟键码
        """
        inputs = []

        # 按下事件
        input_down = INPUT()
        input_down.type = INPUT_KEYBOARD
        input_down.union.ki.wVk = vk_code
        input_down.union.ki.wScan = 0
        input_down.union.ki.dwFlags = 0
        input_down.union.ki.time = 0
        input_down.union.ki.dwExtraInfo = None
        inputs.append(input_down)

        # 释放事件
        input_up = INPUT()
        input_up.type = INPUT_KEYBOARD
        input_up.union.ki.wVk = vk_code
        input_up.union.ki.wScan = 0
        input_up.union.ki.dwFlags = KEYEVENTF_KEYUP
        input_up.union.ki.time = 0
        input_up.union.ki.dwExtraInfo = None
        inputs.append(input_up)

        # 发送输入（带重试机制）
        for attempt in range(self.max_retries):
            try:
                array_type = INPUT * len(inputs)
                input_array = array_type(*inputs)
                result = user32.SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))

                if result == len(inputs):
                    return  # 成功

                error_code = ctypes.get_last_error()
                if attempt < self.max_retries - 1:
                    time.sleep(0.01)
                    continue
                else:
                    raise InputError(
                        f"SendInput 失败: 期望发送 {len(inputs)} 个输入，实际发送 {result} 个, 错误代码: {error_code}"
                    )
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(0.01)
                    continue
                else:
                    raise InputError(f"发送特殊键失败 (VK={vk_code}): {e}")

    def type_text(self, text: Union[str, int, float]):
        """
        输入文本，支持中英文、emoji等所有Unicode字符

        Args:
            text: 要输入的文本字符串（会自动转换为字符串）

        Raises:
            InputError: 输入失败时抛出
            TypeError: 文本类型无法转换时抛出
        """
        # 输入验证和类型转换
        if text is None:
            raise TypeError("文本不能为 None")

        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                raise TypeError(f"无法将 {type(text)} 转换为字符串: {e}")

        if len(text) == 0:
            return  # 空字符串，直接返回

        # 逐字符输入
        for i, char in enumerate(text):
            # 检查是否是特殊字符
            if char == "\n":
                self._send_special_key(VK_RETURN)
            elif char == "\t":
                self._send_special_key(VK_TAB)
            elif char == "\b":
                self._send_special_key(VK_BACK)
            else:
                # 普通字符，包括中文、英文、数字、符号、emoji等
                self._send_unicode_char(char)

            # 延迟
            if self.delay > 0:
                time.sleep(self.delay)

    def press_key(self, key_name: str):
        """
        按下特殊键

        Args:
            key_name: 键名，支持 'enter', 'backspace', 'tab', 'esc', 'space',
                     'left', 'right', 'up', 'down', 'delete', 'shift', 'ctrl', 'alt'

        Raises:
            ValueError: 不支持的键名
        """
        key_map = {
            "enter": VK_RETURN,
            "backspace": VK_BACK,
            "tab": VK_TAB,
            "esc": VK_ESCAPE,
            "escape": VK_ESCAPE,
            "space": VK_SPACE,
            "left": VK_LEFT,
            "right": VK_RIGHT,
            "up": VK_UP,
            "down": VK_DOWN,
            "delete": VK_DELETE,
            "shift": VK_SHIFT,
            "ctrl": VK_CONTROL,
            "control": VK_CONTROL,
            "alt": VK_MENU,
        }

        if not isinstance(key_name, str):
            raise TypeError(f"键名必须是字符串，当前类型: {type(key_name)}")

        key_name_lower = key_name.lower()
        if key_name_lower in key_map:
            self._send_special_key(key_map[key_name_lower])
            if self.delay > 0:
                time.sleep(self.delay)
        else:
            supported_keys = ", ".join(sorted(set(key_map.keys())))
            raise ValueError(f"不支持的键名: '{key_name}'\n支持的键名: {supported_keys}")

    def press_keys(self, *key_names):
        """
        按下多个特殊键

        Args:
            *key_names: 多个键名

        Example:
            press_keys('ctrl', 'a')  # Ctrl+A
        """
        for key_name in key_names:
            self.press_key(key_name)


def type_text(text: Union[str, int, float], delay=0.01):
    """
    便捷函数：输入文本

    Args:
        text: 要输入的文本
        delay: 每个字符之间的延迟（秒）

    Example:
        type_text("abAB123你好")
        type_text("Hello世界！😀", delay=0.02)
    """
    inputter = UnicodeInput(delay=delay)
    inputter.type_text(text)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Windows Unicode 输入测试 - 改进版")
    print("=" * 60)
    print("\n5秒后开始测试...")
    print("请将光标放在任何可输入文本的地方（如记事本、浏览器输入框）\n")
    time.sleep(5)

    # 创建输入器实例
    inputter = UnicodeInput(delay=0.05)

    try:
        print("✓ 测试0: 空格")
        inputter.type_text("")
        time.sleep(1)
        # 测试1：基本混合输入
        print("✓ 测试1: 混合中英文数字")
        inputter.type_text("abAB123你好")
        time.sleep(1)

        # 测试2：更复杂的文本
        print("✓ 测试2: 复杂文本")
        inputter.type_text("Hello世界！Test测试123")
        time.sleep(1)

        # 测试3：Emoji和特殊符号（代理对测试）
        print("✓ 测试3: Emoji和特殊符号")
        inputter.type_text("😀🎉💻🚀 表情符号测试")
        time.sleep(1)

        # 测试4：各种标点符号
        print("✓ 测试4: 标点符号")
        inputter.type_text("中文标点：，。！？；：''（）【】")
        time.sleep(1)

        # 测试5：使用便捷函数
        print("✓ 测试5: 便捷函数")
        type_text("这是便捷函数测试abcABC123", delay=0.03)

        # 测试6：数字自动转换
        print("✓ 测试6: 数字和类型转换")
        inputter.type_text(123456)
        inputter.type_text(" | ")
        inputter.type_text(3.14159)

        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)

    except InputError as e:
        print(f"\n❌ 输入错误: {e}")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback

        traceback.print_exc()
