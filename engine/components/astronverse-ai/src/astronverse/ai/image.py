"""Image AI utilities for text-to-image generation and image understanding."""

import base64
import os
import uuid
from pathlib import Path

import requests
from astronverse.actionlib.logger import logger
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg
from astronverse.ai import AspectRatio, ImageSize, LLMMultiModalModelTypes, VLLMModelTypes
from astronverse.ai.prompt.image import IMAGE_UNDERSTANDING
from astronverse.ai.error import BizException, ERROR_FORMAT

API_URL = "http://127.0.0.1:{}/api/rpa-ai-service/v1/images/generations".format(
    atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
)

CHAT_API_URL = "http://127.0.0.1:{}/api/rpa-ai-service/v1/chat/completions".format(
    atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
)


def _calculate_size_from_ratio(aspect_ratio, base_size) -> str:
    """根据比例和基础尺寸计算实际尺寸"""
    ratio_val = aspect_ratio.value if isinstance(aspect_ratio, AspectRatio) else aspect_ratio
    size_val = base_size.value if isinstance(base_size, ImageSize) else base_size

    ratio_map = {
        "1:1": "1024x1024" if size_val == "1024p" else "720x720",
        "3:4": "768x1024" if size_val == "1024p" else "540x720",
        "4:3": "1024x768" if size_val == "1024p" else "720x540",
        "4:7": "585x1024" if size_val == "1024p" else "411x720",
        "7:4": "1024x585" if size_val == "1024p" else "720x411",
        "9:16": "576x1024" if size_val == "1024p" else "405x720",
        "16:9": "1024x576" if size_val == "1024p" else "720x405",
    }
    return ratio_map.get(ratio_val, "1024x1024")


class ImageAI:
    """Provide image generation and understanding utilities: text-to-image and image-to-text."""

    @staticmethod
    @atomicMg.atomic(
        "ImageAI",
        inputList=[
            atomicMg.param(
                "model_select",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.SELECT.value,
                ),
            ),
            atomicMg.param(
                "prompt",
                formType=AtomicFormTypeMeta(
                    type="INPUT_PYTHON_TEXTAREAMODAL_VARIABLE",
                ),
            ),
            atomicMg.param(
                "image_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [".jpg", ".jpeg", ".png"], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("AI_image_analysis_res", types="Str")],
    )
    def understand_image(
        model_select: VLLMModelTypes = VLLMModelTypes.QWEN_3_VL_32B_Instruct,
        prompt: str = IMAGE_UNDERSTANDING,
        image_path: str = "",
    ) -> str:
        """
        图像理解
        Args:
            - model_select(LLMMultiModalModelTypes): 模型选择
            - prompt(str): 提示词（≤5000字符）
            - image_path(str): 图片路径（支持.jpg/.jpeg/.png，≤20MB）
        Return:
            `str`, 图像理解生成结果
        """
        # 参数验证
        if not prompt:
            raise BizException("提示词不能为空", "prompt is required")

        if len(prompt) > 5000:
            raise BizException("提示词超出最大限制5000字符", "prompt exceeds 5000 characters")

        if not image_path:
            raise BizException("图片路径不能为空", "image_path is required")

        # 验证文件存在
        if not os.path.exists(image_path):
            raise BizException(f"图片文件不存在: {image_path}", "image file not found")

        # 验证文件大小
        file_size = os.path.getsize(image_path)
        if file_size > 20 * 1024 * 1024:  # 20MB
            raise BizException("图片大小超过20MB限制", "image size exceeds 20MB")

        # 验证文件格式
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in [".jpg", ".jpeg", ".png"]:
            raise BizException(f"不支持的图片格式: {file_ext}", "unsupported image format")

        # 获取模型值
        model = model_select.value if isinstance(model_select, VLLMModelTypes) else model_select

        try:
            # 读取图片并转换为base64
            with open(image_path, "rb") as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # 确定MIME类型
            mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"

            # 构建请求数据（OpenAI Vision API格式）
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                            },
                        ],
                    }
                ],
                "stream": False,
            }

            # 调用 API
            response = requests.post(CHAT_API_URL, json=data, timeout=360)
            response.raise_for_status()

            response_json = response.json()

            # 解析响应
            if "choices" in response_json and len(response_json["choices"]) > 0:
                message = response_json["choices"][0].get("message", {})
                content = message.get("content", "")
                return content
            elif "data" in response_json and "choices" in response_json["data"]:
                # 兼容新格式
                message = response_json["data"]["choices"][0].get("message", {})
                content = message.get("content", "")
                return content
            else:
                raise BizException("响应格式不正确", "invalid response format")

        except requests.exceptions.Timeout:
            raise BizException("图像理解超时，请稍后重试", "image understanding timeout")
        except requests.exceptions.RequestException as e:
            raise BizException(ERROR_FORMAT.format(e), f"API request failed: {str(e)}")
        except Exception as e:
            raise BizException(ERROR_FORMAT.format(e), f"Image understanding failed: {str(e)}")

    @staticmethod
    @atomicMg.atomic(
        "ImageAI",
        inputList=[
            atomicMg.param(
                "model_select",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.SELECT.value,
                ),
            ),
            atomicMg.param(
                "prompt",
                formType=AtomicFormTypeMeta(
                    type="INPUT_PYTHON_TEXTAREAMODAL_VARIABLE",
                ),
            ),
            atomicMg.param(
                "negative_prompt",
                formType=AtomicFormTypeMeta(
                    type="INPUT_PYTHON_TEXTAREAMODAL_VARIABLE",
                ),
                required=False,
            ),
            atomicMg.param(
                "aspect_ratio",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.SELECT.value,
                ),
            ),
            atomicMg.param(
                "image_size",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.SELECT.value,
                ),
            ),
            atomicMg.param(
                "image_output_path",
                formType=AtomicFormTypeMeta(
                    type="INPUT_VARIABLE_PYTHON_FILE",
                    params={"file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "image_filename",
                formType=AtomicFormTypeMeta(
                    type="INPUT_VARIABLE_PYTHON",
                ),
            ),
        ],
    )
    def generate_image(
        model_select: LLMMultiModalModelTypes = LLMMultiModalModelTypes.QWEN_IMAGE_2512,
        prompt: str = "",
        negative_prompt: str = "",
        aspect_ratio: AspectRatio = AspectRatio.RATIO_1_1,
        image_size: ImageSize = ImageSize.SIZE_1024P,
        image_output_path: str = "",
        image_filename: str = "AI_image_res",
    ) -> str:
        """
        文生图
        Args:
            - model_select(LLMMultiModalModelTypes): 模型选择
            - prompt(str): 正向提示词（≤5000字符）
            - negative_prompt(str): 负向提示词（≤5000字符）
            - aspect_ratio(AspectRatio): 图片比例
            - image_size(ImageSize): 图片大小
            - image_output_path(str): 图片输出路径
            - image_filename(str): 图片名称
        """
        # 参数验证
        if not prompt:
            raise BizException("提示词不能为空", "prompt is required")

        if len(prompt) > 5000:
            raise BizException("提示词超出最大限制5000字符", "prompt exceeds 5000 characters")

        if negative_prompt and len(negative_prompt) > 5000:
            raise BizException("负向提示词超出最大限制5000字符", "negative_prompt exceeds 5000 characters")

        # 获取模型值
        model = model_select.value if isinstance(model_select, LLMMultiModalModelTypes) else model_select

        # 计算实际尺寸
        size = _calculate_size_from_ratio(aspect_ratio, image_size)

        # 构建请求数据
        data = {
            "model": model,
            "prompt": prompt,
            "size": size,
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        # 添加可选的 patch_id（某些模型需要）
        data["patch_id"] = "0"

        try:
            # 调用 API
            response = requests.post(API_URL, json=data, timeout=360)

            response.raise_for_status()

            response_json = response.json()

            # 处理响应（rpa-ai-service 返回 b64_json 格式）
            if "data" in response_json and len(response_json["data"]) > 0:
                image_data = response_json["data"][0]

                # 确保输出目录存在
                output_dir = Path(image_output_path)
                output_dir.mkdir(parents=True, exist_ok=True)

                # 生成文件名（添加随机ID避免冲突）
                random_id = str(uuid.uuid4())[:8]
                filename = f"{image_filename}_{random_id}.png"
                file_path = output_dir / filename

                if "b64_json" in image_data:
                    # 星辰 MaaS 返回 base64 编码图像
                    image_bytes = base64.b64decode(image_data["b64_json"])
                    file_path.write_bytes(image_bytes)

                elif "url" in image_data:
                    # 兼容 URL 格式
                    img_response = requests.get(image_data["url"], timeout=60)
                    img_response.raise_for_status()
                    file_path.write_bytes(img_response.content)

                else:
                    raise BizException("响应中未找到图像数据", "image data not found in response")

            else:
                raise BizException("响应格式不正确", "invalid response format")

        except requests.exceptions.Timeout:
            raise BizException("图像生成超时，请稍后重试", "image generation timeout")
        except requests.exceptions.RequestException as e:
            raise BizException(ERROR_FORMAT.format(e), f"API request failed: {str(e)}")
        except Exception as e:
            raise BizException(ERROR_FORMAT.format(e), f"Image generation failed: {str(e)}")
