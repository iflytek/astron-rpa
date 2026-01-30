"""
凭证管理服务

使用 keyring 库安全存储密码凭证
"""

import json
from typing import Optional

import keyring
import keyring.errors
from astronverse.scheduler.logger import logger

# 服务名称，用于 keyring 存储
SERVICE_NAME = "AstronRPA"

# 索引 key，用于存储所有凭证名称
INDEX_KEY = "__credential_index__"

# 空密码哨兵值，用于区分"空密码"和"不存在"
EMPTY_PASSWORD_SENTINEL = "__RPA__Credential__EMPTY__PASSWORD__"


class CredentialService:
    """凭证管理服务"""

    # ---------- 内部工具方法 ----------

    @staticmethod
    def _encode_password(password: str) -> str:
        """确保存储到 keyring 的密码永不为空"""
        return EMPTY_PASSWORD_SENTINEL if password == "" else password

    @staticmethod
    def _decode_password(stored: Optional[str]) -> Optional[str]:
        """从 keyring 取出后还原真实密码"""
        if stored is None:
            return None
        if stored == EMPTY_PASSWORD_SENTINEL:
            return ""
        return stored

    @staticmethod
    def _get_index() -> list[str]:
        """获取凭证名称索引"""
        try:
            raw = keyring.get_password(SERVICE_NAME, INDEX_KEY)
            if not raw:
                return []
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            logger.exception(f"获取凭证索引失败: {e}")
            return []

    @staticmethod
    def _save_index(names: list[str]):
        """保存凭证名称索引"""
        try:
            keyring.set_password(SERVICE_NAME, INDEX_KEY, json.dumps(sorted(set(names))))
        except Exception as e:
            logger.exception(f"保存凭证索引失败: {e}")

    @staticmethod
    def _cleanup_index():
        """
        清理 index 中已被手动删除的凭证
        只在读取类操作时触发，不影响性能
        """
        names = CredentialService._get_index()
        valid = []

        for name in names:
            stored = keyring.get_password(SERVICE_NAME, name)
            if stored is not None:
                valid.append(name)

        if valid != names:
            CredentialService._save_index(valid)

    # ---------- 对外 API ----------

    @staticmethod
    def list_credentials() -> list[dict]:
        """
        获取所有凭证名称列表（自动修复索引）

        Returns:
            凭证名称列表，如 [{"name": "admin_password"}, {"name": "db_connection"}]
        """
        try:
            CredentialService._cleanup_index()
            return [{"name": name} for name in CredentialService._get_index()]
        except Exception as e:
            logger.exception(f"获取凭证列表失败: {e}")
            return []

    @staticmethod
    def create_credential(name: str, password: str) -> bool:
        """
        创建凭证

        Args:
            name: 凭证名称
            password: 凭证密码（可以为空字符串）

        Returns:
            是否创建成功

        Raises:
            ValueError: 如果凭证已存在
        """
        try:
            if CredentialService.exists(name):
                raise ValueError(f"凭证 '{name}' 已存在")

            # 编码密码（处理空密码情况）
            encoded = CredentialService._encode_password(password)
            keyring.set_password(SERVICE_NAME, name, encoded)

            # 更新索引
            names = CredentialService._get_index()
            names.append(name)
            CredentialService._save_index(names)

            logger.info(f"凭证 '{name}' 创建成功")
            return True
        except ValueError:
            raise
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
            # 删除密码（即使不存在也不报错）
            try:
                keyring.delete_password(SERVICE_NAME, name)
            except keyring.errors.PasswordDeleteError:
                pass

            # 更新索引
            names = CredentialService._get_index()
            if name in names:
                names.remove(name)
                CredentialService._save_index(names)

            logger.info(f"凭证 '{name}' 删除成功")
            return True
        except Exception as e:
            logger.exception(f"删除凭证失败: {e}")
            return False

    @staticmethod
    def exists(name: str) -> bool:
        """
        检查凭证是否存在（只以 keyring 为准，不信索引）

        Args:
            name: 凭证名称

        Returns:
            凭证是否存在
        """
        try:
            stored = keyring.get_password(SERVICE_NAME, name)
            return stored is not None
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
            凭证密码（不存在返回 None，存在可返回空字符串）
        """
        try:
            stored = keyring.get_password(SERVICE_NAME, name)
            return CredentialService._decode_password(stored)
        except Exception as e:
            logger.exception(f"获取凭证失败: {e}")
            return None
