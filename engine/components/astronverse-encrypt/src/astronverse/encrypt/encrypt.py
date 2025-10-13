"""面向原子框架的加密能力封装。

包装 `EncryptCore` 的底层实现为原子（atomicMg）可调用形式，
提供 MD5 / SHA / AES 及 Base64 编解码原子能力。
"""

import os

from astronverse.actionlib import (
    AtomicFormType,
    AtomicFormTypeMeta,
    AtomicLevel,
    DynamicsItem,
)
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.utils import FileExistenceType, handle_existence
from astronverse.encrypt import Base64CodeType, EncryptCaseType, MD5bitsType, SHAType
from astronverse.encrypt.core import EncryptCore


class Encrypt:  # pylint: disable=too-few-public-methods
    """对外暴露的加密原子集合。

    通过 atomic 装饰器将底层实现包装成流程可编排的原子节点。所有方法均为
    无状态静态方法，便于测试与复用。
    """

    @staticmethod
    @atomicMg.atomic("Encrypt", outputList=[atomicMg.param("md5_encrypted_result", types="Str")])
    def md5_encrypt(
        source_str: str,
        md5_method: MD5bitsType = MD5bitsType.MD5_32,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """MD5 摘要。

        参数:
            source_str: 待加密字符串。
            md5_method: 32 / 16 位输出。
            case_method: 大小写控制。
        返回: 计算后的 MD5 字符串（或空字符串当 source_str 为空）。
        """
        if source_str:
            md5_encrypted_result = EncryptCore.md5_encrypt(source_str, md5_method, case_method)
            return md5_encrypted_result
        return ""

    @staticmethod
    @atomicMg.atomic("Encrypt", outputList=[atomicMg.param("sha_encrypted_result", types="Str")])
    def sha_encrypt(
        source_str: str,
        sha_method: SHAType = SHAType.SHA1,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """SHA / SHA3 摘要。

        参数:
            source_str: 待处理字符串
            sha_method: 算法类型 (SHA1 / SHA2 / SHA3*)
            case_method: 大小写控制
        返回: 结果字符串（或空字符串）。
        """
        if source_str:
            sha_encrypted_result = EncryptCore.sha_encrypt(source_str, sha_method, case_method)
            return sha_encrypted_result
        return ""

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        outputList=[atomicMg.param("symmetric_encrypted_result", types="Str")],
    )
    def symmetric_encrypt(source_str: str, password: str = "") -> str:
        """AES 对称加密（CBC）。"""
        if source_str:
            symmetric_encrypted_result = EncryptCore.symmetric_encrypt(source_str, password)
            return symmetric_encrypted_result
        return ""

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        outputList=[atomicMg.param("symmetric_decrypted_result", types="Str")],
    )
    def symmetric_decrypt(source_str: str, password: str = "") -> str:
        """AES 对称解密（CBC）。"""
        if source_str:
            symmetric_decrypted_result = EncryptCore.symmetric_decrypt(source_str, password)
            return symmetric_decrypted_result
        return ""

    # --------------Base64操作-----------------
    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        inputList=[
            atomicMg.param(
                "string_data",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.string_data.show",
                        expression=(f"return $this.encode_type.value == '{Base64CodeType.STRING.value}'"),
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression=(f"return $this.encode_type.value == '{Base64CodeType.PICTURE.value}'"),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("encoded_string", types="Str")],
    )
    def base64_encoding(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ):
        """Base64 编码原子能力包装。

        - STRING: 直接对 `string_data` 编码
        - PICTURE: 读取 `file_path` 文件并编码为 data URI
        """
        if encode_type == Base64CodeType.PICTURE and not os.path.exists(file_path):
            raise ValueError("图片文件不存在!")
        encoded_string = EncryptCore.base64_encode(encode_type, string_data, file_path)
        return encoded_string

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        inputList=[
            atomicMg.param(
                "file_path",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression=(f"return $this.decode_type.value == '{Base64CodeType.PICTURE.value}'"),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression=(f"return $this.decode_type.value == '{Base64CodeType.PICTURE.value}'"),
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                level=AtomicLevel.ADVANCED,
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression=(f"return $this.decode_type.value == '{Base64CodeType.PICTURE.value}'"),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("decoded_string", types="Str")],
    )
    def base64_decoding(
        decode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """Base64 解码原子能力包装。

        - STRING: 返回解码后的字符串
        - PICTURE: 写入文件（处理同名策略）后返回最终文件路径
        """
        new_file_path: str = (
            os.path.join(file_path, f"{file_name}.png") if decode_type == Base64CodeType.PICTURE else ""
        )
        if new_file_path:
            # handle_existence 可能返回 None，使用短路保留原值
            new_file_path = handle_existence(new_file_path, exist_handle_type) or new_file_path
        decoded_string = EncryptCore.base64_decode(
            decode_type,
            string_data,
            new_file_path,
        )
        return decoded_string
