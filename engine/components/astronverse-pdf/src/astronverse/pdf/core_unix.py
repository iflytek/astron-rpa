from astronverse.pdf.core import IPDFCore


class PDFCore(IPDFCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "linux {}".format(msg)
