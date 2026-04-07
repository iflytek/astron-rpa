"""Ticket and card OCR client."""

import base64
from typing import Any, Optional

from fastapi import UploadFile

from app.logger import get_logger
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import TICKET_OCR_CONFIG
from app.utils.ocr.error_policy import classify_ocr_failure

logger = get_logger(__name__)


class TicketOCRClient(XFYunOCRClient):
    """Client for ticket and card recognition using XunFei OCR API."""

    def __init__(self):
        super().__init__(TICKET_OCR_CONFIG)

    def _build_request_payload(self, image_base64: str, ocr_type: str, encoding: str = "jpg") -> dict[str, Any]:
        """构建请求负载.

        Args:
            image_base64: Base64编码的图片数据
            ocr_type: OCR类型，如 air_itinerary(行程单), train_ticket(火车票), taxi_receipt(出租车票)等
            encoding: 图片编码格式
        """
        return {
            "header": {"app_id": self.auth_strategy.app_id, "status": 3},
            "parameter": {
                "ocr": {
                    "type": ocr_type,
                    "level": 1,
                    "result": {"encoding": "utf8", "compress": "raw", "format": "json"},
                }
            },
            "payload": {"image": {"encoding": encoding, "status": 3, "image": image_base64}},
        }

    async def recognize(
        self, file: Optional[UploadFile] = None, image_url: Optional[str] = None, ocr_type: str = "air_itinerary"
    ) -> dict[str, Any]:
        """识别票据卡证.

        Args:
            file: 上传的图片文件
            image_url: 图片URL
            ocr_type: OCR类型
        """
        if not file and not image_url:
            raise OCRError("Either file or image_url must be provided")

        # 读取图片并编码
        if file:
            image_data = await file.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            encoding = "jpg" if file.content_type in ["image/jpeg", "image/jpg"] else "png"
        else:
            # TODO: 支持从URL下载图片
            raise OCRError("Image URL is not supported yet")

        # 构建请求
        payload = self._build_request_payload(image_base64, ocr_type, encoding)

        # 发起请求
        response = await self._make_request("POST", self.config.base_url, json=payload)
        result = response.json()

        # 检查响应
        header = result.get("header", {})
        if header.get("code") != 0:
            error_msg = header.get("message", "Unknown error")
            decision = classify_ocr_failure(header.get("code"), error_msg)
            raise OCRError(
                error_msg,
                code=header.get("code"),
                should_deduct_points=decision.should_deduct_points,
                status_code=decision.http_status,
                category=decision.category.value,
            )

        # 解析结果
        payload_result = result.get("payload", {}).get("result", {})
        text_base64 = payload_result.get("text", "")

        if text_base64:
            text_json = base64.b64decode(text_base64).decode("utf-8")
            import json
            return json.loads(text_json)

        return {}
