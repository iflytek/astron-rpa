from astronverse.smart.core.core import ISmartCore


class SmartCore(ISmartCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "linux {}".format(msg)
