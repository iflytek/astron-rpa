"""Client for xcAgent flow execution (Xingchen API streaming wrapper)."""

import http.client
import json
import os

import requests
from astronverse.baseline.logger.logger import logger


class xcAgent:  # pylint: disable=invalid-name
    """Minimal client for Xingchen flow execution.

    NOTE: Class name kept for backward compatibility; consider renaming to `XcAgent`.
    """

    def __init__(self, api_key: str, api_secret: str):
        """Store credentials and prepare headers."""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": "Bearer {}:{}".format(api_key, api_secret),
        }
        self.upload_headers = {
            "Authorization": "Bearer {}:{}".format(api_key, api_secret),
            # 加这个会出错 "Content-Type": "multipart/form-data"
        }

    def run_flow(self, flow_id, content, is_stream, file_flag, variable_name, variable_value, file_path):
        if not variable_name:
            parameters = {"AGENT_USER_INPUT": content}
        else:
            if file_flag:
                # 上传文件
                response = self.upload_file(file_path)
                file_url = response.json()["data"]["url"]
                parameters = {"AGENT_USER_INPUT": content, variable_name: file_url}
            else:
                parameters = {"AGENT_USER_INPUT": content, variable_name: variable_value}
        logger.info("parameters: {}".format(parameters))

        data = {
            "flow_id": flow_id,
            "parameters": parameters,
            "stream": is_stream,
        }
        payload = json.dumps(data)

        conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=120)
        conn.request(
            "POST",
            "/workflow/v1/chat/completions",
            payload,
            self.headers,
            encode_chunked=True,
        )
        res = conn.getresponse()

        data = res.readline().decode("utf-8")
        response_json = json.loads(data)
        logger.info("response_json: {}".format(response_json))
        return response_json["choices"][0]["delta"]["content"]

    @staticmethod
    def get_content_type(file_path):
        """获取文件的Content-Type"""
        import mimetypes

        local_mime_types = {
            # 图片
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".svg": "image/svg+xml",
            # 文档
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            # Excel
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".csv": "text/csv",
            # 文本
            ".txt": "text/plain",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            # 压缩文件
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
            ".7z": "application/x-7z-compressed",
            # 音视频
            ".mp3": "audio/mpeg",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".wav": "audio/wav",
        }

        _, ext = os.path.splitext(str(file_path))
        extension = ext.lower()

        # 首先尝试从预定义映射获取
        if extension in local_mime_types:
            return local_mime_types[extension]

        # 尝试使用系统的mimetypes模块
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type

        # 默认返回二进制流
        return "application/octet-stream"

    def upload_file(self, file_path):
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_name = os.path.basename(file_path)

        # 获取Content-Type
        content_type = self.get_content_type(file_path)
        logger.info(f"文件类型: {content_type}")

        with open(file_path, "rb") as f:
            # 构建files参数
            files = {"file": (file_name, f, content_type)}

            try:
                response = requests.post(
                    "https://xingchen-api.xf-yun.com/workflow/v1/upload_file",
                    files=files,
                    headers=self.upload_headers,
                    timeout=300,  # 5分钟超时，适应大文件
                )

                response.raise_for_status()
                logger.info(f"上传成功: {response.json()}")
                return response

            except requests.exceptions.RequestException as e:
                logger.info(f"上传失败: {e}")
                raise


if __name__ == "__main__":
    api_key = "2075eb7e0dd13201048ae915b0083741"
    api_secret = "Zjc4ZjJiZjJmODI3ZjI4MTc0ZTUyNjI2"
    agent = xcAgent(api_key, api_secret)
    agent.upload_file(r"C:\Users\zyzhou23\Downloads\RPAAI.pdf")
