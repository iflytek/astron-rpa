from astronverse.excel.core import IExcelCore


class ExcelCore(IExcelCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return f"linux {msg}"
