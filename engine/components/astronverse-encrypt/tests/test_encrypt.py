from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from astronverse.encrypt import Base64CodeType
from astronverse.encrypt.core import EncryptCore
from astronverse.encrypt.encrypt import Encrypt


class TestEncrypt(TestCase):
    def test_base64_encrypt(self):
        encrypt = Encrypt()
        plain_text = "Hello World"
        encrypted_text = encrypt.base64_encoding(encode_type=Base64CodeType.STRING, string_data=plain_text)
        assert encrypted_text == "SGVsbG8gV29ybGQ="

    def test_md5_encrypt(self):
        enc = EncryptCore()
        plain_text = "Hello World"
        encrypted_text = enc.md5_encrypt(source_str=plain_text)
        assert encrypted_text == "b10a8db164e0754105b7a99be72e3fe5"

    def test_base64_encode(self):
        enc = EncryptCore()
        plain_text = "Hello World"
        encrypted_text = enc.base64_encode(
            encode_type=Base64CodeType.STRING, string_data=plain_text, file_path="./not-used.txt"
        )
        assert encrypted_text == "SGVsbG8gV29ybGQ="

    def test_picture_encoding_reads_only_the_selected_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            path.write_bytes(b"synthetic-image")
            result = EncryptCore.base64_encode(
                encode_type=Base64CodeType.PICTURE, string_data="ignored", file_path=str(path)
            )
            assert result == "data:image/png;base64,c3ludGhldGljLWltYWdl"
