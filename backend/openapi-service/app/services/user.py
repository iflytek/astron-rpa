from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate
from typing import Optional
from redis.asyncio import Redis
from datetime import datetime
import pytz
from app.logger import get_logger
import httpx
import json

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession, redis: Redis = None, api_key_service=None):
        self.db = db
        self.redis = redis
        self.api_key_service = api_key_service
        self.register_api_url = "http://robot-service:8004/api/robot/register"

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
                logger.info(f"调用外部注册接口，phone: {phone}, url: {url}")

                # 发送 POST 请求
                response = await client.post(url, timeout=10.0)

                # 检查 HTTP 状态码
                if response.status_code != 200:
                    logger.error(
                        f"外部接口返回异常状态码，phone: {phone}, status_code: {response.status_code}, response: {response.text}"
                    )
                    return None

                # 解析返回数据
                response_data = response.json()
                logger.info(
                    f"外部接口返回数据，phone: {phone}, response: {json.dumps(response_data, ensure_ascii=False)}"
                )

                # 提取完整的用户信息
                user_data = response_data.get("data", {})
                user_id = user_data.get("userId")
                if not user_id:
                    logger.error(f"外部接口返回数据中缺少 userId，phone: {phone}")
                    return None

                logger.info(f"外部接口返回成功，phone: {phone}, user_id: {user_id}")
                return user_data

        except httpx.TimeoutException as e:
            logger.error(f"调用外部接口超时，phone: {phone}, error: {str(e)}")
            return None
        except httpx.RequestError as e:
            logger.error(f"调用外部接口请求错误，phone: {phone}, error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析外部接口返回数据失败，phone: {phone}, error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"调用外部接口发生异常，phone: {phone}, error: {str(e)}")
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
            logger.info(f"用户已存在，phone: {phone}, user_id: {existing_user.user_id}")
            return {
                "user_id": existing_user.user_id,
                "api_key": existing_user.default_api_key,
            }

        # 调用外部接口获取user_id及相关信息
        logger.info(f"开始注册新用户，phone: {phone}")
        user_data = await self._call_register_api(phone)

        if not user_data:
            logger.error(f"外部接口调用失败，phone: {phone}")
            return None

        user_id = user_data.get("userId")

        # 生成默认API Key
        default_api_key = None
        if self.api_key_service:
            try:
                api_key_data = ApiKeyCreate(name=f"default_key_{phone}")
                default_api_key = await self.api_key_service.create_api_key(api_key_data, user_id)
                logger.info(f"为用户生成默认API Key，user_id: {user_id}")
            except Exception as e:
                logger.error(f"生成API Key失败，user_id: {user_id}, error: {str(e)}")
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

        logger.info(f"用户注册成功，phone: {phone}, user_id: {user_id}")

        # 返回包含 User 对象和完整用户数据的字典
        return {
            "user_id": user_id,
            "api_key": default_api_key,
            "password": user_data.get("password"),
            "url": user_data.get("url"),
            "account": user_data.get("account"),
        }

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
