from enum import Enum


class MD5bitsType(Enum):
    MD5_32 = "32"
    MD5_16 = "16"


class EncryptCaseType(Enum):
    LOWER = "lower"
    UPPER = "upper"


class SHAType(Enum):
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
    STRING = "string"
    PICTURE = "picture"
