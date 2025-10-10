from unittest import TestCase

from astronverse.encrypt import Base64CodeType
from astronverse.encrypt.encrypt import Encrypt


class TestEncrypt(TestCase):
    def test_base64_encrypt(self):
        encrypt = Encrypt()
        plain_text = "Hello World"
        encrypted_text = encrypt.base64_encoding(encode_type=Base64CodeType.STRING, string_data=plain_text)
        print(encrypted_text)
