"""PDF OCR client for PDF document recognition."""

import asyncio
from typing import Any, Optional

from fastapi import UploadFile

from app.logger import get_logger
from app.schemas.ocr import PDFOCRResponsePayload
from app.utils.ocr.base import OCRError, XFYunOCRClient
from app.utils.ocr.config import PDF_OCR_CONFIG
from app.utils.ocr.error_policy import classify_ocr_failure

logger = get_logger(__name__)


def _extract_pdf_error_message(result: dict[str, Any]) -> str:
    for key in ("desc", "message", "msg", "errorMsg", "detail"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Unknown error"


class PDFOCRClient(XFYunOCRClient):
    """Client for PDF document OCR using XunFei OCR LLM."""

    def __init__(self):
        super().__init__(PDF_OCR_CONFIG)
        self.poll_interval = 5  # 轮询间隔（秒）
        self.max_poll_time = 300  # 最大轮询时间（秒）

    async def _create_task(
        self, file: Optional[UploadFile] = None, pdf_url: Optional[str] = None, export_format: str = "json"
    ) -> dict[str, Any]:
        """创建 PDF OCR 任务."""
        if not file and not pdf_url:
            raise OCRError("Either file or pdf_url must be provided")

        url = f"{self.config.base_url}/start"

        if file:
            # 上传文件
            file_content = await file.read()
            files = {"file": (file.filename, file_content, file.content_type)}
            data = {"exportFormat": export_format}

            response = await self._make_request("POST", url, data=data, files=files)
        else:
            # URL 模式也按 multipart/form-data 提交
            files = {
                "pdfUrl": (None, pdf_url),
                "exportFormat": (None, export_format),
            }
            response = await self._make_request("POST", url, files=files)

        result = response.json()

        # 检查响应状态 (flag 是布尔值)
        if not result.get("flag"):
            error_msg = _extract_pdf_error_message(result)
            decision = classify_ocr_failure(result.get("code"), error_msg)
            raise OCRError(
                error_msg,
                code=result.get("code"),
                should_deduct_points=decision.should_deduct_points,
                status_code=decision.http_status,
                category=decision.category.value,
            )

        return result.get("data", {})

    async def _query_task_status(self, task_no: str) -> dict[str, Any]:
        """查询任务状态."""
        url = f"{self.config.base_url}/status"
        params = {"taskNo": task_no}

        response = await self._make_request("GET", url, params=params)
        result = response.json()

        if not result.get("flag"):
            error_msg = _extract_pdf_error_message(result)
            decision = classify_ocr_failure(result.get("code"), error_msg)
            raise OCRError(
                error_msg,
                code=result.get("code"),
                should_deduct_points=decision.should_deduct_points,
                status_code=decision.http_status,
                category=decision.category.value,
            )

        return result.get("data", {})

    async def _poll_task_completion(self, task_no: str) -> dict[str, Any]:
        """轮询任务直到完成."""
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.max_poll_time:
                raise OCRError(f"Task polling timeout after {self.max_poll_time} seconds")

            task_data = await self._query_task_status(task_no)
            status = task_data.get("status")

            logger.info(f"Task {task_no} status: {status}")

            # 状态：CREATE, DOING, FINISH, FAIL
            if status == "FINISH":
                return task_data
            elif status == "FAIL":
                decision = classify_ocr_failure("TASK_FAIL", f"Task {task_no} failed")
                raise OCRError(
                    f"Task {task_no} failed",
                    code="TASK_FAIL",
                    should_deduct_points=decision.should_deduct_points,
                    status_code=decision.http_status,
                    category=decision.category.value,
                )

            # 等待后继续轮询
            await asyncio.sleep(self.poll_interval)

    async def recognize(
        self, file: Optional[UploadFile] = None, pdf_url: Optional[str] = None, export_format: str = "json"
    ) -> PDFOCRResponsePayload:
        """
        识别 PDF 文档.

        Args:
            file: 上传的 PDF 文件
            pdf_url: PDF 文件的公网 URL
            export_format: 导出格式 (word, markdown, json)

        Returns:
            PDFOCRResponsePayload: 识别结果 payload

        Raises:
            OCRError: 识别失败时抛出
        """
        try:
            # 创建任务
            task_data = await self._create_task(file, pdf_url, export_format)
            task_no = task_data.get("taskNo")

            if not task_no:
                raise OCRError("Failed to get task number from response")

            logger.info(f"Created PDF OCR task: {task_no}")

            # 轮询任务完成
            completed_data = await self._poll_task_completion(task_no)

            # 构建响应
            response = PDFOCRResponsePayload(
                task_no=task_no,
                status=completed_data.get("status", "unknown"),
                page_count=len(completed_data.get("pageList", [])) if completed_data.get("pageList") else 0,
                result_url=completed_data.get("downUrl"),
            )

            logger.info(f"PDF OCR task {task_no} completed with {response.page_count} pages")
            return response

        except Exception as e:
            logger.error(f"PDF OCR processing failed: {e}")
            raise
