"""Document OCR client for general document recognition using OCR LLM."""

import json
from typing import Any

from app.logger import get_logger
from app.schemas.ocr import DocumentOCRResponse
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import DOCUMENT_OCR_CONFIG
from app.utils.ocr.error_policy import classify_ocr_failure

logger = get_logger(__name__)


class DocumentOCRClient(XFYunOCRClient):
    """Client for general document OCR using XunFei OCR LLM."""

    def __init__(self):
        super().__init__(DOCUMENT_OCR_CONFIG)

    def _build_request_payload(
        self, image_base64: str, encoding: str = "jpg", output_level: int = 1, output_format: str = "markdown"
    ) -> dict[str, Any]:
        """构建请求 payload."""
        # result_format 必须是组合值，如 "json", "json,markdown", "json,sed" 等
        # 默认使用 "json,markdown"
        if output_format == "markdown":
            result_format = "json,markdown"
        elif output_format == "json":
            result_format = "json"
        else:
            result_format = output_format

        return {
            "header": {
                "app_id": self.auth_strategy.app_id,
                "status": 0,  # 0: 开始, 1: 继续, 2: 结束
            },
            "parameter": {
                "ocr": {
                    "result_option": "normal",
                    "result_format": result_format,
                    "output_type": "one_shot",
                    "result": {"encoding": "utf8", "compress": "raw", "format": "plain"},
                }
            },
            "payload": {
                "image": {
                    "encoding": encoding,
                    "image": image_base64,
                    "status": 0,  # 0: 开始, 1: 继续, 2: 结束
                    "seq": 0,
                }
            },
        }

    async def recognize(
        self, image_base64: str, encoding: str = "jpg", output_level: int = 1, output_format: str = "markdown"
    ) -> DocumentOCRResponse:
        """
        识别文档图像.

        Args:
            image_base64: Base64 编码的图像
            encoding: 图像格式 (jpg, png, etc.)
            output_level: 输出级别 (1-3)
            output_format: 输出格式 (markdown, json, etc.)

        Returns:
            DocumentOCRResponse: 识别结果

        Raises:
            OCRError: 识别失败时抛出
        """
        try:
            payload = self._build_request_payload(image_base64, encoding, output_level, output_format)

            response = await self._make_request("POST", self.config.base_url, json=payload)

            result = response.json()
            model = DocumentOCRResponse.model_validate(result)

            if model.header.code != 0:
                error_message = model.header.message or "Unknown API error"
                decision = classify_ocr_failure(model.header.code, error_message)
                raise OCRError(
                    error_message,
                    code=model.header.code,
                    should_deduct_points=decision.should_deduct_points,
                    status_code=decision.http_status,
                    category=decision.category.value,
                )

            logger.info("Document OCR processing completed successfully")
            return model

        except Exception as e:
            logger.error(f"Document OCR processing failed: {e}")
            raise
