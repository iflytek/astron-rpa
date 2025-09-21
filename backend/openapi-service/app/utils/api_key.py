import secrets
import string
import bcrypt
from app.logger import get_logger

logger = get_logger(__name__)
class APIKeyUtils:

    @staticmethod
    def generate_api_key(length=32):
        # 可选字符集：大小写字母 + 数字
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def hash_api_key(api_key):
        # 生成盐 + 哈希
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_api_key(input_key, hashed_key):
        logger.info(f"input_key: {input_key}, hashed_key: {hashed_key}")
        return bcrypt.checkpw(input_key.encode('utf-8'), hashed_key.encode('utf-8'))