"""Client wrapper for Dify API: file upload and workflow execution."""

import mimetypes
import os

import requests
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

                response = requests.post(upload_url, headers=self.headers, files=files, data=data)
                if response.status_code == 201:  # 201 表示创建成功
                    logger.info("文件上传成功")
                    return response.json().get("id")  # 获取上传的文件 ID
                else:
                    logger.info(f"文件上传失败，状态码: {response.status_code}")
                    return None
        except Exception as e:
            logger.info(f"发生错误: {str(e)}")
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
            response = requests.post(workflow_url, headers=self.headers, json=data)
            if response.status_code == 200:
                logger.info("工作流执行成功")
                return response.json()
            else:
                logger.info(f"工作流执行失败，状态码: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to execute workflow, status code: {response.status_code}",
                }
        except Exception as e:
            logger.info(f"发生错误: {str(e)}")
            return {"status": "error", "message": str(e)}

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
            response = requests.post(chatflow_url, headers=self.headers, json=data)
            if response.status_code == 200:
                logger.info("工作流执行成功")
                return response.json()
            else:
                logger.info(f"工作流执行失败，状态码: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to execute workflow, status code: {response.status_code}",
                }
        except Exception as e:
            logger.info(f"发生错误: {str(e)}")
            return {"status": "error", "message": str(e)}
