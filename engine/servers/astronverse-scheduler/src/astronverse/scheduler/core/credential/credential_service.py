"""
凭证管理服务

使用 keyring 库安全存储密码凭证
"""

import keyring
from astronverse.scheduler.logger import logger

# 服务名称，用于 keyring 存储
SERVICE_NAME = "astronverse-rpa"


class CredentialService:
    """凭证管理服务"""

    @staticmethod
    def list_credentials() -> list[dict]:
        """
        获取所有凭证名称列表

        Returns:
            凭证名称列表，如 [{"name": "admin_password"}, {"name": "db_connection"}]
        """
        try:
            # keyring 不提供列出所有凭证的功能，需要自己维护一个凭证名称列表
            # 使用一个特殊的 key 来存储所有凭证名称
            names_str = keyring.get_password(SERVICE_NAME, "__credential_names__")
            if not names_str:
                return []
            names = names_str.split(",")
            return [{"name": name} for name in names if name]
        except Exception as e:
            logger.exception(f"获取凭证列表失败: {e}")
            return []

    @staticmethod
    def create_credential(name: str, password: str) -> bool:
        """
        创建或更新凭证

        Args:
            name: 凭证名称
            password: 凭证密码

        Returns:
            是否创建成功
        """
        try:
            # 存储密码
            keyring.set_password(SERVICE_NAME, name, password)

            # 更新凭证名称列表
            names_str = keyring.get_password(SERVICE_NAME, "__credential_names__")
            if names_str:
                names = set(names_str.split(","))
            else:
                names = set()
            names.add(name)
            keyring.set_password(SERVICE_NAME, "__credential_names__", ",".join(names))

            logger.info(f"凭证 '{name}' 创建成功")
            return True
        except Exception as e:
            logger.exception(f"创建凭证失败: {e}")
            return False

    @staticmethod
    def delete_credential(name: str) -> bool:
        """
        删除凭证

        Args:
            name: 凭证名称

        Returns:
            是否删除成功
        """
        try:
            # 删除密码
            keyring.delete_password(SERVICE_NAME, name)

            # 更新凭证名称列表
            names_str = keyring.get_password(SERVICE_NAME, "__credential_names__")
            if names_str:
                names = set(names_str.split(","))
                names.discard(name)
                if names:
                    keyring.set_password(SERVICE_NAME, "__credential_names__", ",".join(names))
                else:
                    keyring.delete_password(SERVICE_NAME, "__credential_names__")

            logger.info(f"凭证 '{name}' 删除成功")
            return True
        except Exception as e:
            logger.exception(f"删除凭证失败: {e}")
            return False

    @staticmethod
    def exists(name: str) -> bool:
        """
        检查凭证是否存在

        Args:
            name: 凭证名称

        Returns:
            凭证是否存在
        """
        try:
            password = keyring.get_password(SERVICE_NAME, name)
            return password is not None
        except Exception as e:
            logger.exception(f"检查凭证是否存在失败: {e}")
            return False

    @staticmethod
    def get_credential(name: str) -> str | None:
        """
        获取凭证密码（供内部使用）

        Args:
            name: 凭证名称

        Returns:
            凭证密码，如果不存在则返回 None
        """
        try:
            return keyring.get_password(SERVICE_NAME, name)
        except Exception as e:
            logger.exception(f"获取凭证失败: {e}")
            return None

