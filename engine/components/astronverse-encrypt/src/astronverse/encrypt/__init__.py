"""加密相关公开枚举类型。

暴露常用加密/编码操作时需要的枚举选择项，供外部调用统一引用，避免魔法字符串散落。
"""

from enum import Enum

__all__ = [
    "Base64CodeType",
    "EncryptCaseType",
    "MD5bitsType",
    "SHAType",
]


class MD5bitsType(Enum):
    """MD5 输出位数枚举。

    - MD5_32: 标准 32 位十六进制表示
    - MD5_16: 传统裁剪（取 32 位中间 16 位）表示
    """

    MD5_32 = "32"
    MD5_16 = "16"


class EncryptCaseType(Enum):
    """加密输出大小写控制。"""

    LOWER = "lower"
    UPPER = "upper"


class SHAType(Enum):
    """SHA 系列算法类型。包括 SHA1 / SHA2 / SHA3 各常见变种。"""

    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_224 = "sha3_224"
    SHA3_256 = "sha3_256"
    SHA3_384 = "sha3_384"
    SHA3_512 = "sha3_512"


class Base64CodeType(Enum):
    """Base64 输入/输出数据类型抽象。"""

    STRING = "string"
    PICTURE = "picture"
