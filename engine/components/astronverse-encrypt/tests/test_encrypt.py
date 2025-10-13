from unittest import TestCase

from astronverse.encrypt import Base64CodeType
from astronverse.encrypt.core import EncryptCore
from astronverse.encrypt.encrypt import Encrypt


class TestEncrypt(TestCase):
    def test_base64_encrypt(self):
        encrypt = Encrypt()
        plain_text = "Hello World"
        encrypted_text = encrypt.base64_encoding(encode_type=Base64CodeType.STRING, string_data=plain_text)
        print(encrypted_text)

    def test_md5_encrypt(self):
        enc = EncryptCore()
        plain_text = "Hello World"
        encrypted_text = enc.md5_encrypt(source_str=plain_text)
        print(encrypted_text)

    def test_base64_encode(self):
        enc = EncryptCore()
        plain_text = "Hello World"
        encrypted_text = enc.base64_encode(encode_type=Base64CodeType.STRING, string_data=plain_text, file_path='./a.txt')
        print(encrypted_text)


