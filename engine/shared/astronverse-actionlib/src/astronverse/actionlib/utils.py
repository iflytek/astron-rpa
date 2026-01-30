import ast
import inspect
import os
from enum import Enum
from typing import Optional
import keyring
from astronverse.actionlib.error import *
from astronverse.actionlib.logger import logger


# 凭据服务名称，用于 keyring 存储
SERVICE_NAME = "AstronRPA"

# 空密码哨兵值，用于区分"空密码"和"不存在"
EMPTY_PASSWORD_SENTINEL = "__RPA__Credential__EMPTY__PASSWORD__"


class Credential:
    """凭证读取服务"""

    @staticmethod
    def _decode_password(stored: Optional[str]) -> Optional[str]:
        """从 keyring 取出后还原真实密码"""
        if stored is None:
            return None
        if stored == EMPTY_PASSWORD_SENTINEL:
            return ""
        return stored

    @staticmethod
    def get_credential(name: str) -> str | None:
        """
        获取凭证密码（供内部使用）

        Args:
            name: 凭证名称

        Returns:
            凭证密码（不存在返回 None，存在可返回空字符串）
        """
        try:
            stored = keyring.get_password(SERVICE_NAME, name)
            return Credential._decode_password(stored)
        except Exception as e:
            logger.exception(f"获取凭证失败: {e}")
            return None


class InspectType(Enum):
    EMPTY = "empty"
    PYTHONBASE = "python_base"
    QUOTE = "quote"
    TYPING = "typing"
    ENUM = "enum"
    RPABASE = "rpa_base"
    OTHER = "other"


class FileExistenceType(Enum):
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CANCEL = "cancel"


def gen_type(__annotation__):
    if __annotation__ == inspect.Parameter.empty:
        # 类型空
        types = "Any"
        kind = InspectType.EMPTY
    elif __annotation__ in [str, list, tuple, int, float, dict, bool]:
        # 基础变量
        types = (
            __annotation__.__name__.capitalize() if getattr(__annotation__, "__name__", "_empty") != "_empty" else None
        )
        kind = InspectType.PYTHONBASE
    elif isinstance(__annotation__, str):
        # 引号类型
        types = __annotation__
        kind = InspectType.QUOTE
    elif str(__annotation__).startswith("typing."):
        # typing.Optional|Union|Any
        types = "Any"
        kind = InspectType.TYPING
        logger.warning("type not support: {}".format(__annotation__))
    elif issubclass(__annotation__, Enum):
        # Enum类型
        types = __annotation__.__name__ if getattr(__annotation__, "__name__", "_empty") != "_empty" else None
        kind = InspectType.ENUM
    elif hasattr(__annotation__, "__validate__"):
        # pydantic基础类型扩展
        types = __annotation__.__name__ if getattr(__annotation__, "__name__", "_empty") != "_empty" else None
        kind = InspectType.RPABASE
    else:
        # 其他类型
        types = "Any"
        kind = InspectType.OTHER
        logger.warning("type not support: {}".format(__annotation__))
    return types, kind


def handle_existence(file_path, exist_type):
    # 文件存在时的处理方式
    if exist_type.value == FileExistenceType.OVERWRITE.value:
        # 覆盖已存在文件，直接返回文件路径
        return file_path
    elif exist_type.value == FileExistenceType.RENAME.value:
        if os.path.exists(file_path):
            full_file_name = os.path.basename(file_path)
            file_name, file_ext = os.path.splitext(full_file_name)
            count = 1
            while True:
                new_full_file_name = f"{file_name}_{count}{file_ext}"
                new_file_path = os.path.join(os.path.dirname(file_path), new_full_file_name)
                if os.path.exists(new_file_path):
                    count += 1
                else:
                    return new_file_path
        return file_path
    elif exist_type.value == FileExistenceType.CANCEL.value:
        if os.path.exists(file_path):
            return ""
        else:
            return file_path
    logger.info("类型匹配失败，原路返回文件路径：{}".format(file_path))
    return file_path


class ParamModel:
    def __init__(self, inputList: list, key: str = ""):
        self.inputList = inputList
        self.key = key

    @staticmethod
    def parse_conditional(conditional, kwargs) -> bool:
        """解析conditional"""
        res = []
        for i in conditional.operands:
            left = None
            if i.left in kwargs:
                left = kwargs[i.left]

            # > < == != >= <= in
            if i.operator == ">":
                res.append(bool(float(left) > float(i.right)))
            elif i.operator == "<":
                res.append(bool(float(left) < float(i.right)))
            elif i.operator == "==":
                res.append(bool(left == i.right))
            elif i.operator == "!=":
                res.append(bool(left != i.right))
            elif i.operator == ">=":
                res.append(bool(float(left) >= float(i.right)))
            elif i.operator == "<=":
                res.append(bool(float(left) <= float(i.right)))
            elif i.operator == "in":
                res.append(bool(left in i.right))
            else:
                raise BaseException(TYPE_KIND_ERROR_FORMAT.format(i.operator), "类型错误{}".format(i.operator))

        # and or
        if conditional.operators == "and":
            return all(res)
        elif conditional.operators == "or":
            return any(res)
        else:
            raise BaseException(
                TYPE_KIND_ERROR_FORMAT.format(conditional.operators), "类型错误{}".format(conditional.operators)
            )

    def __call__(self, **kwargs) -> dict:
        res_list = {}
        for i in self.inputList:
            if i.name in kwargs:
                value = kwargs[i.name]
            else:
                continue

            # 类型处理
            if i.__annotation__ == inspect.Parameter.empty:
                # 忽略
                pass
            elif i.__annotation__ in [str, list, tuple, int, float, dict, bool]:
                try:
                    if i.__annotation__ == bool and isinstance(value, str):
                        if value.lower() in ["false", "none", "undefined", ""]:
                            value = False
                        else:
                            value = i.__annotation__(value)
                    elif i.__annotation__ in [int, float] and isinstance(value, str):
                        if value.lower() == "":
                            value = 0
                        else:
                            value = i.__annotation__(value)
                    elif (
                        i.__annotation__ == list
                        and isinstance(value, str)
                        and value.startswith("[")
                        and value.endswith("]")
                    ) or (
                        i.__annotation__ == dict
                        and isinstance(value, str)
                        and value.startswith("{")
                        and value.endswith("}")
                    ):
                        value = ast.literal_eval(value)
                    else:
                        value = i.__annotation__(value)
                except Exception as e:
                    raise ParamException(
                        PARAM_CONVERT_ERROR_FORMAT.format(i.name, i.types, value),
                        "{}的值转换成{}失败{}, error:{}".format(i.name, i.types, value, e),
                    ) from e
            elif isinstance(i.__annotation__, str) or str(i.__annotation__).startswith("typing."):
                # 忽略
                pass
            elif issubclass(i.__annotation__, Enum):
                # 转换
                for a in i.__annotation__:
                    if a.value == value:
                        value = a
            elif hasattr(i.__annotation__, "__validate__"):
                # 转换
                try:
                    value = i.__annotation__.__validate__(i.name, value)
                except Exception as e:
                    raise ParamException(
                        PARAM_CONVERT_ERROR_FORMAT.format(i.name, i.types, value),
                        "{}的值装换成{}失败{}, error:{}".format(i.name, i.types, value, e),
                    ) from e
            else:
                # 忽略
                pass
            res_list[i.name] = value
        return res_list
