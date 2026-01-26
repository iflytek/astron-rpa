import json
from datetime import datetime
from typing import Optional

import httpx
import pytz
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import get_logger
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession, redis: Redis = None, api_key_service=None):
        self.db = db
        self.redis = redis
        self.api_key_service = api_key_service
        self.register_api_url = "http://robot-service:8004/api/robot/register"
        self.user_info_api_url = "http://robot-service:8004/api/robot/astron-agent/get-user-id"

    async def _call_register_api(self, phone: str) -> str:
        """
        调用外部接口进行用户注册

        入参: phone (手机号)
        出参: user_id (用户ID)

        外部接口返回格式:
        {
          "code": "000000",
          "data": {
           "userId":"1cb222f6-6ae1-4d6e-a8d7-709374c02821",
            "account": "1234567890",
            "password": "y3#J3vm!4hJ8k2v",
            "url":"https://xxxxxxxxxxx"
          },
          "message": ""
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                # 构建请求 URL
                url = f"{self.register_api_url}?phone={phone}"
                logger.info("调用外部注册接口，phone: %s, url: %s", phone, url)

                # 发送 POST 请求
                response = await client.post(url, timeout=10.0)

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    logger.error(
                        "外部接口返回异常状态码，phone: %s, status_code: %s, response: %s",
                        phone,
                        response.status_code,
                        response.text,
                    )
                    return None

                # 解析返回数据
                response_data = response.json()
                logger.info(
                    "外部接口返回数据，phone: %s, response: %s",
                    phone,
                    json.dumps(response_data, ensure_ascii=False),
                )

                # 提取完整的用户信息
                user_data = response_data.get("data", {})
                user_id = user_data.get("userId")
                if not user_id:
                    logger.error("外部接口返回数据中缺少 userId，phone: %s", phone)
                    return None

                logger.info("外部接口返回成功，phone: %s, user_id: %s", phone, user_id)
                return user_data

        except httpx.TimeoutException as e:
            logger.exception("调用外部接口超时，phone: %s", phone)
            return None
        except httpx.RequestError as e:
            logger.exception("调用外部接口请求错误，phone: %s", phone)
            return None
        except json.JSONDecodeError as e:
            logger.exception("解析外部接口返回数据失败，phone: %s", phone)
            return None
        except Exception as e:
            logger.exception("调用外部接口发生异常，phone: %s", phone)
            return None

    async def _call_user_info_api(self, phone: str) -> Optional[dict]:
        """
        调用外部接口进行用户注册

        入参: phone (手机号)
        出参: user_id (用户ID)

        外部接口返回格式:
        {
          "code": "000000",
          "data": {
            "userId":"1cb222f6-6ae1-4d6e-a8d7-709374c02821",
          },
          "message": ""
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                # 使用基础URL，通过JSON传递phone参数
                url = self.user_info_api_url
                logger.info("调用外部注册接口，phone: %s, url: %s", phone, url)

                # 发送 POST 请求，phone通过JSON传递
                response = await client.post(
                    url, json={"phone": phone}, headers={"X-API-Key": "opensource666!"}, timeout=10.0
                )

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    logger.error(
                        "外部接口返回异常状态码，phone: %s, status_code: %s, response: %s",
                        phone,
                        response.status_code,
                        response.text,
                    )
                    return None

                # 解析返回数据
                response_data = response.json()
                logger.info(
                    "外部接口返回数据，phone: %s, response: %s",
                    phone,
                    json.dumps(response_data, ensure_ascii=False),
                )
                if response_data.get("code") == "500000":
                    logger.error("查询用户信息报错，%s", response_data.get("message"))
                    return None

                # 提取完整的用户信息
                user_data = response_data.get("data", {})
                user_id = user_data.get("userId", None)
                if not user_id:
                    logger.error("外部接口返回数据中缺少 userId，phone: %s", phone)
                    return None

                logger.info("外部接口返回成功，phone: %s, user_id: %s", phone, user_id)
                return user_data

        except httpx.TimeoutException as e:
            logger.exception("调用外部接口超时，phone: %s", phone)
            return None
        except httpx.RequestError as e:
            logger.exception("调用外部接口请求错误，phone: %s", phone)
            return None
        except json.JSONDecodeError as e:
            logger.exception("解析外部接口返回数据失败，phone: %s", phone)
            return None
        except Exception as e:
            logger.exception("调用外部接口发生异常，phone: %s", phone)
            return None

    async def register_user(self, phone: str) -> Optional[dict]:
        """
        用户注册方法

        入参: phone (手机号)
        出参: dict 包含 User 对象和外部接口返回的完整用户数据

        流程:
        1. 根据手机号查询用户是否存在
        2. 如果存在，返回用户信息
        3. 如果不存在，调用外部接口获取user_id及相关信息
        4. 生成默认API Key
        5. 创建新用户并保存到数据库
        """
        # 查询手机号是否已存在
        query = select(User).where(User.phone == phone)
        result = await self.db.execute(query)
        existing_user = result.scalars().first()

        # 如果用户已存在，直接返回
        if existing_user:
            logger.info("用户已存在，phone: %s, user_id: %s", phone, existing_user.user_id)
            return {
                "user_id": existing_user.user_id,
                "api_key": existing_user.default_api_key,
            }

        # 调用外部接口获取user_id及相关信息
        logger.info("开始注册新用户，phone: %s", phone)
        user_data = await self._call_register_api(phone)

        if not user_data:
            logger.error("外部接口调用失败，phone: %s", phone)
            return None

        user_id = user_data.get("userId")

        # 生成默认API Key
        default_api_key = None
        if self.api_key_service:
            try:
                api_key_data = ApiKeyCreate(name=f"default_key_{phone}")
                default_api_key = await self.api_key_service.create_api_key(api_key_data, user_id)
                logger.info("为用户生成默认API Key，user_id: %s", user_id)
            except Exception as e:
                logger.exception("生成API Key失败，user_id: %s", user_id)
                # API Key生成失败不影响用户创建

        # 创建新用户 (只保存 user_id、phone、default_api_key)
        new_user = User(
            user_id=user_id,
            phone=phone,
            default_api_key=default_api_key,
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
        )

        # 保存到数据库
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)

        logger.info("用户注册成功，phone: %s, user_id: %s", phone, user_id)

        # 返回包含 User 对象和完整用户数据的字典
        return {
            "user_id": user_id,
            "api_key": default_api_key,
            "password": user_data.get("password"),
            "url": user_data.get("url"),
            "account": user_data.get("account"),
        }

    async def get_user_info(self, phone: str) -> Optional[dict]:
        """
        获取用户信息

        入参: phone (手机号)
        出参: user_id

        """
        # 查询手机号是否已存在
        query = select(User).where(User.phone == phone)
        result = await self.db.execute(query)
        existing_user = result.scalars().first()

        # 如果用户已存在，直接返回
        if existing_user:
            logger.info("用户已存在，phone: %s, user_id: %s", phone, existing_user.user_id)
            return {
                "user_id": existing_user.user_id,
                "api_key": existing_user.default_api_key,
            }

        # 调用外部接口获取user_id及相关信息
        logger.info("开始获取新用户，phone: %s", phone)
        user_data = await self._call_user_info_api(phone)

        if not user_data:
            logger.error("外部接口调用失败，phone: %s", phone)
            return None

        user_id = user_data.get("userId")

        # 生成默认API Key
        default_api_key = None
        if self.api_key_service:
            try:
                api_key_data = ApiKeyCreate(name=f"default_key_{phone}")
                default_api_key = await self.api_key_service.create_api_key(api_key_data, user_id)
                logger.info("为用户生成默认API Key，user_id: %s", user_id)
            except Exception as e:
                logger.exception("生成API Key失败，user_id: %s", user_id)
                # API Key生成失败不影响用户创建

        # 创建新用户 (只保存 user_id、phone、default_api_key)
        new_user = User(
            user_id=user_id,
            phone=phone,
            default_api_key=default_api_key,
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
        )

        # 保存到数据库
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)

        logger.info("用户获取key成功，phone: %s, user_id: %s", phone, user_id)

        # 返回包含 User 对象和完整用户数据的字典
        return {"user_id": user_id, "api_key": default_api_key}

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户信息"""
        query = select(User).where(User.phone == phone)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        """根据user_id获取用户信息"""
        query = select(User).where(User.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()
