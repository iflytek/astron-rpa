"""Business license OCR client."""

import base64
from typing import Any

from fastapi import UploadFile

from app.logger import get_logger
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import BUSINESS_LICENSE_CONFIG
from app.utils.ocr.error_policy import classify_ocr_failure

logger = get_logger(__name__)


class BusinessLicenseOCRClient(XFYunOCRClient):
    """Client for business license recognition using XunFei OCR API."""

    def __init__(self):
        super().__init__(BUSINESS_LICENSE_CONFIG)

    async def recognize(self, file: UploadFile) -> dict[str, Any]:
        """识别营业执照.

        Args:
            file: 上传的图片文件
        """
        # 读取图片并编码
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # 发起请求（使用表单数据）
        data = {"image": image_base64}
        response = await self._make_request("POST", self.config.base_url, data=data)
        result = response.json()

        # 检查响应
        code = result.get("code")
        if code != "0":
            error_msg = result.get("desc", "Unknown error")
            decision = classify_ocr_failure(code, error_msg)
            raise OCRError(
                error_msg,
                code=code,
                should_deduct_points=decision.should_deduct_points,
                status_code=decision.http_status,
                category=decision.category.value,
            )

        return result.get("data", {})
