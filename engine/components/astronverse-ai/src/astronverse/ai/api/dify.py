"""Client wrapper for Dify API: file upload and workflow execution."""

import mimetypes
import os
from typing import Optional

import requests
from astronverse.baseline.logger.logger import logger

mimetypes.add_type("text/markdown", ".md")


class Dify:
    """Lightweight client for interacting with Dify platform APIs."""

    base_url = "https://api.dify.ai/v1/"

    def __init__(self, api_key: str):
        """Initialize client with API key."""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            # "Content-Type": "application/json"
        }

    def upload_file(self, file_path: str, user: str) -> Optional[str]:
        """Upload a file to Dify and return file id or None on failure."""
        upload_url = self.base_url + "files/upload"

        try:
            logger.info("上传文件中...")
            mime_type, _ = mimetypes.guess_type(file_path)

            file_extension = os.path.splitext(file_path)[1].replace(".", "").upper()
            with open(file_path, "rb") as file:
                # requests files 参数: {'field': (filename, fileobj, content_type)}
                # files 采用二元组 (filename, fileobj); 若需要 MIME 可保留三元组
                files = {
                    "file": (
                        os.path.basename(file_path),
                        file,  # type: ignore[arg-type]
                    )
                }
                data = {"user": user, "type": file_extension}  # 设置文件类型为扩展名

                response = requests.post(
                    upload_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=30,
                )
                if response.status_code == 201:  # 201 表示创建成功
                    logger.info("文件上传成功")
                    return response.json().get("id")  # 获取上传的文件 ID
                logger.warning("文件上传失败，状态码: %s", response.status_code)
                return None
        except Exception as e:
            logger.error("文件上传异常: %s", e)
            return None

    def run_workflow(
        self,
        user: str,
        variable_name: str,
        file_flag: bool,
        variable_value,
        file_type: str,
        response_mode: str = "blocking",
    ) -> dict:
        """Run a workflow with given inputs and return execution result dict."""
        workflow_url = self.base_url + "workflows/run"
        if file_flag:
            template = {
                "transfer_method": "local_file",
                "upload_file_id": variable_value,
                "type": file_type,
            }
        else:
            template = variable_value

        data = {
            "inputs": {variable_name: template},
            "response_mode": response_mode,
            "user": user,
        }

        try:
            logger.info("运行工作流...")
            response = requests.post(
                workflow_url,
                headers=self.headers,
                json=data,
                timeout=60,
            )
            if response.status_code == 200:
                logger.info("工作流执行成功")
                return response.json()
            logger.warning("工作流执行失败，状态码: %s", response.status_code)
            return {
                "status": "error",
                "message": f"Failed to execute workflow, status code: {response.status_code}",
            }
        except Exception as e:
            logger.error("工作流执行异常: %s", e)
            return {"status": "error", "message": str(e)}
