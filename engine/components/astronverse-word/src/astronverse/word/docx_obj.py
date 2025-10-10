from typing import Any
from astronverse.actionlib.error import PARAM_VERIFY_ERROR_FORMAT


class DocumentObject:
    def __init__(self, document_object: Any):
        self.document_object = document_object

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, DocumentObject):
            return value
        raise BaseException(
            PARAM_VERIFY_ERROR_FORMAT.format(name, value),
            f"{name}参数验证失败{value}",
        )
