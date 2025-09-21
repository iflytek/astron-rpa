from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import json
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode
from app.schemas.chat import ChatCompletionParam, ChatPromptParam
from app.services.point import PointTransactionType
from app.dependencies.points import PointChecker, PointsContext
from app.config import get_settings
from app.utils.prompt import prompt_dict, format_prompt, get_available_prompts
from urllib.parse import urljoin

API_KEY = get_settings().AICHAT_API_KEY
API_ENDPOINT = urljoin(get_settings().AICHAT_BASE_URL, "chat/completions")

logger = get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["统一大模型接口"],
)


@router.post("/completions")
async def chat_completions(
    params: ChatCompletionParam,
    points_context: PointsContext = Depends(
        PointChecker(
            get_settings().AICHAT_POINTS_COST, PointTransactionType.AICHAT_COST
        ),
    ),
):
    logger.info("Processing chat completion request...")
    logger.info(f"Request params: {params}")
    # 构造请求参数
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = params.model_dump(exclude_none=True)

    logger.info(f"Request headers: {headers}")
    logger.info(f"Request params.stream: {params.stream}")
    # 处理请求
    try:
        if params.stream:
            response = await handle_stream_request(headers, data)
        else:
            response = await handle_non_stream_request(headers, data)

        # 处理成功，扣除积分
        await points_context.deduct_points()
        # 返回响应
        return response
    except HTTPException as e:
        logger.warning(f"HTTP error: {e.detail}")
        raise e
    except Exception:
        logger.error("Internal server error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_stream_request(headers, data):
    """处理流式请求"""
    response_meta = {"media_type": "text/event-stream"}

    async def stream_response():
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST",
                    API_ENDPOINT,
                    headers=headers,
                    json=data,
                ) as upstream_response:
                    upstream_response.raise_for_status()
                    response_meta["media_type"] = upstream_response.headers.get(
                        "content-type", "text/event-stream"
                    )
                    async for chunk in upstream_response.aiter_raw():
                        yield chunk
            except httpx.HTTPStatusError as e:
                # 上游API错误
                logger.warning(f"Upstream API error: {e.response.status_code}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Upstream API error: {e.response.status_code}",
                )
            except Exception as e:
                # 其他错误
                logger.error(f"Request error: {str(e)}")
                raise e

    return StreamingResponse(
        content=stream_response(),
        media_type=response_meta["media_type"],
    )


long_timeout = httpx.Timeout(
    connect=10.0,     # 连接超时：10秒
    read=360.0,       # 读取超时：6分钟
    write=10.0,       # 写入超时：10秒
    pool=320.0        # 总超时：6分20秒
)

async def handle_non_stream_request(headers, data):
    """处理非流式请求"""
    async with httpx.AsyncClient(timeout=long_timeout) as client:
        try:
            upstream_response = await client.post(
                API_ENDPOINT,
                headers=headers,
                json=data,
            )
            upstream_response.raise_for_status()

            return Response(
                content=upstream_response.content,
                media_type=upstream_response.headers.get("content-type"),
                status_code=upstream_response.status_code,
            )
        except httpx.HTTPStatusError as e:
            # 上游API错误
            logger.warning(f"Upstream API error: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Upstream API error: {e.response.status_code}",
            )
        except Exception as e:
            # 其他错误
            logger.error(f"Request error: {str(e)}")
            raise e

@router.post("/prompt")
async def chat_prompt(
    params: ChatPromptParam,
    points_context: PointsContext = Depends(
        PointChecker(
            get_settings().AICHAT_POINTS_COST, PointTransactionType.AICHAT_COST
        ),
    ),
):
    """
    根据预设prompt调用大模型对话
    """
    logger.info(f"Processing chat prompt request: {params.prompt_type}")
    
    # 检查prompt类型是否存在
    if params.prompt_type not in prompt_dict:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown prompt type: {params.prompt_type}. Available types: {get_available_prompts()}"
        )
    
    # 格式化prompt
    try:
        formatted_prompt = format_prompt(params.prompt_type, params.params or {})
        logger.info(f"Formatted prompt: {formatted_prompt[:100]}...")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 构造消息
    messages = [
        {
            "role": "user",
            "content": formatted_prompt
        }
    ]
    
    # 构造请求参数
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": params.model,
        "messages": messages,
        "stream": params.stream,
    }
    
    logger.info(f"Request data: {data}")
    
    # 处理请求
    try:
        if params.stream:
            response = await handle_stream_request(headers, data)
            # 处理成功，扣除积分
            await points_context.deduct_points()

            # 这里如果是流式，交给客户端自行处理
            return response
        else:
            response = await handle_non_stream_request(headers, data)
            await points_context.deduct_points()
            if isinstance(response.body, bytes):
                content_str = response.body.decode('utf-8')
            else:
                content_str = response.body

            # 解析 JSON
            data = json.loads(content_str)

            # 如果是非流式，解析成标准相应，data里是完整结果
            return StandardResponse(
                code=ResCode.SUCCESS,
                msg="调用 {} prompt 成功".format(params.prompt_type),
                data=data["choices"][0]["message"]["content"]
            )

    except HTTPException as e:
        logger.warning(f"HTTP error: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    