"""核心加密实现函数集合。

包含 MD5、SHA、AES 对称加解密以及 Base64 编码/解码等基础能力。
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable
from pathlib import Path

from astronverse.encrypt import (
    Base64CodeType,
    EncryptCaseType,
    MD5bitsType,
    SHAType,
)
from Cryptodome.Cipher import AES


class EncryptCore:  # pylint: disable=too-few-public-methods
    """静态加密工具类。所有方法为纯函数式，不依赖实例状态。"""

    # ---- Hash 系列 ----
    @staticmethod
    def md5_encrypt(
        source_str: str,
        md5_method: MD5bitsType = MD5bitsType.MD5_32,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """对字符串进行 MD5 摘要。

        参数:
            source_str: 待处理字符串。
            md5_method: 16 或 32 位输出。
            case_method: 输出大小写控制。
        """
        md5_obj = hashlib.md5()
        md5_obj.update(source_str.encode("utf8"))

        if md5_method == MD5bitsType.MD5_32:
            digest = md5_obj.hexdigest()
        else:  # MD5_16
            digest = md5_obj.hexdigest()[8:-8]

        if case_method == EncryptCaseType.UPPER:
            return digest.upper()
        return digest.lower()

    @staticmethod
    def sha_encrypt(
        source_str: str,
        sha_method: SHAType = SHAType.SHA1,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """对字符串进行 SHA (* 与 SHA3 *) 摘要。

        使用字典映射减少分支并避免可能的未定义变量。"""
        sha_map: dict[SHAType, Callable[[], hashlib._Hash]] = {
            SHAType.SHA1: hashlib.sha1,
            SHAType.SHA224: hashlib.sha224,
            SHAType.SHA256: hashlib.sha256,
            SHAType.SHA384: hashlib.sha384,
            SHAType.SHA512: hashlib.sha512,
            SHAType.SHA3_224: hashlib.sha3_224,
            SHAType.SHA3_256: hashlib.sha3_256,
            SHAType.SHA3_384: hashlib.sha3_384,
            SHAType.SHA3_512: hashlib.sha3_512,
        }
        sha_func = sha_map[sha_method]
        sha_obj = sha_func()
        sha_obj.update(source_str.encode("utf8"))
        digest = sha_obj.hexdigest()
        if case_method == EncryptCaseType.UPPER:
            return digest.upper()
        return digest.lower()

    # ---- AES 对称加密 ----
    @staticmethod
    def symmetric_encrypt(source_str: str, password: str = "") -> str:
        """使用 AES-CBC 模式对称加密。

        密钥与 IV 直接来源于 password（经补齐到 16 的倍数）。"""

        def pad16(value: str) -> bytes:
            while len(value.encode("utf-8")) % 16 != 0:
                value += "\0"
            return value.encode("utf-8")

        if not source_str:
            raise ValueError("加密对象不能为空!")
        if not isinstance(source_str, str):  # 防御式
            raise ValueError("请提供字符串类型对象！")

        password = str(password)
        iv = password
        aes = AES.new(pad16(password), AES.MODE_CBC, pad16(iv))
        encrypt_aes = aes.encrypt(pad16(source_str))
        return str(base64.b64encode(encrypt_aes), encoding="utf-8")

    @staticmethod
    def symmetric_decrypt(source_str: str, password: str = "") -> str:
        """AES-CBC 解密。输入需为 Base64 编码后的密文。"""

        def pad16(value: str) -> bytes:
            while len(value.encode("utf-8")) % 16 != 0:
                value += "\0"
            return value.encode("utf-8")

        if not source_str:
            raise ValueError("解密对象不能为空!")
        if not isinstance(source_str, str):
            raise ValueError("请提供字符串类型对象！")

        password = str(password)
        iv = password
        aes = AES.new(pad16(password), AES.MODE_CBC, pad16(iv))
        base64_decrypted = base64.decodebytes(source_str.encode("utf-8"))
        return str(aes.decrypt(base64_decrypted), encoding="utf-8").replace("\0", "")

    # ---- Base64 ----
    @staticmethod
    def base64_encode(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ) -> str:
        """Base64 编码。可处理字符串或文件。

        当 encode_type == PICTURE 时，会增加 data URI 前缀。"""
        if file_path:
            input_content = Path(file_path).read_bytes()
        else:
            input_content = string_data.encode("utf-8")
        base64_encoded = base64.b64encode(input_content)
        result = base64_encoded.decode("utf-8")
        if encode_type == Base64CodeType.PICTURE:
            return f"data:image/png;base64,{result}"
        return result

    @staticmethod
    def base64_decode(
        decode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ) -> str:
        """Base64 解码。

        当 decode_type == PICTURE 且提供 file_path 时，将解码后的图片写入文件并返回文件路径。
        否则返回解码后的字符串。"""

        def pad4(value: str) -> str:
            return value + "=" * ((4 - len(value) % 4) % 4)

        if decode_type == Base64CodeType.STRING:
            decoded = base64.b64decode(pad4(string_data))
            return str(decoded, "utf-8")

        if file_path:
            Path(file_path).write_bytes(base64.b64decode(string_data.replace("data:image/png;base64,", "")))
        return file_path
