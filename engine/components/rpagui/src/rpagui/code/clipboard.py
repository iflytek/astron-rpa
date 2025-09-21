import pyperclip


class Clipboard:
    """目前只对字符串有效"""

    @staticmethod
    def copy(data: str = ""):
        """
        设置剪切板
        :param data:
        :return:
        """
        return pyperclip.copy(data)

    @staticmethod
    def paste() -> str:
        """
        获取剪切板
        :return:
        """
        return pyperclip.paste()

    @staticmethod
    def clear():
        """
        清空剪切板
        :return:
        """
        return pyperclip.copy("")
