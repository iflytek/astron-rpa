"""Client wrapper for Dify API: file upload and workflow execution."""

import mimetypes
import os

from astronverse.ai.api.http import request_json
from astronverse.baseline.logger.logger import logger

mimetypes.add_type("text/markdown", ".md")


class Dify:
    """Lightweight client for interacting with Dify platform APIs."""

    def __init__(self, api_key, app_url):
        self.api_key = api_key
        if not app_url.endswith("/"):
            app_url += "/"
        self.base_url = app_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            # "Content-Type": "application/json"
        }

    def upload_file(self, file_path, user):
        upload_url = self.base_url + "files/upload"

        try:
            logger.info("上传文件中...")
            mime_type, _ = mimetypes.guess_type(file_path)

            file_extension = os.path.splitext(file_path)[1].replace(".", "").upper()
            with open(file_path, "rb") as file:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        file,
                        mime_type,
                    )  # 确保文件以适当的MIME类型上传
                }
                data = {"user": user, "type": file_extension}  # 设置文件类型为扩展名

                result = request_json("POST", upload_url, headers=self.headers, files=files, data=data)
                return result.get("id")

        except Exception:
            logger.info("AI request failed")
            raise RuntimeError("AI_REQUEST_FAILED") from None

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

        if not variable_name:
            inputs = {}
        else:
            if file_flag:
                template = {
                    "transfer_method": "local_file",
                    "upload_file_id": variable_value,
                    "type": file_type,
                }
            else:
                template = variable_value
            inputs = {variable_name: template}

        data = {
            "inputs": inputs,
            "response_mode": response_mode,
            "user": user,
        }

        try:
            logger.info("运行工作流...")
            return request_json("POST", workflow_url, headers=self.headers, json=data)

        except Exception:
            logger.info("AI request failed")
            raise RuntimeError("AI_REQUEST_FAILED") from None

    def run_chatflow(
        self,
        user,
        query,
        variable_name,
        file_flag,
        variable_value,
        file_type,
        response_mode="blocking",
    ):
        chatflow_url = self.base_url + "chat-messages"

        if not variable_name:
            inputs = {}
        else:
            if file_flag:
                template = {
                    "transfer_method": "local_file",
                    "upload_file_id": variable_value,
                    "type": file_type,
                }
            else:
                template = variable_value
            inputs = {variable_name: template}

        data = {"inputs": inputs, "response_mode": response_mode, "user": user, "query": query, "conversation_id": ""}

        try:
            logger.info("运行工作流...")
            return request_json("POST", chatflow_url, headers=self.headers, json=data)

        except Exception:
            logger.info("AI request failed")
            raise RuntimeError("AI_REQUEST_FAILED") from None
