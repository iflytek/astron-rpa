"""Client for xcAgent flow execution (Xingchen API streaming wrapper)."""

import http.client
import json
import os

from astronverse.ai.api.http import request_json
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
                file_url = self.upload_file(file_path)["data"]["url"]
                parameters = {"AGENT_USER_INPUT": content, variable_name: file_url}
            else:
                parameters = {"AGENT_USER_INPUT": content, variable_name: variable_value}
        return self._run(flow_id, parameters, is_stream)

    def run_astron_flow(self, flow_id, is_stream, inputs):
        parameters = {}
        for item in inputs or []:
            key, value = item["key"], item["value"]
            if item.get("type") == "file":
                value = self.upload_file(value)["data"]["url"]
            parameters[key] = value
        return self._run(flow_id, parameters, is_stream)

    def _run(self, flow_id, parameters, is_stream):
        conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=35)
        try:
            conn.request(
                "POST",
                "/workflow/v1/chat/completions",
                json.dumps({"flow_id": flow_id, "parameters": parameters, "stream": is_stream}),
                self.headers,
            )
            response = conn.getresponse()
            if response.status != 200:
                raise RuntimeError("AI_REQUEST_FAILED")
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise RuntimeError("AI_RESPONSE_TOO_LARGE")
            if is_stream:
                parts = []
                for line in data.decode("utf-8").splitlines():
                    if line.startswith("data:") and line[5:].strip() != "[DONE]":
                        parts.append(json.loads(line[5:])["choices"][0]["delta"].get("content", ""))
                return "".join(parts)
            result = json.loads(data)
            choice = result["choices"][0]
            return choice.get("message", choice.get("delta", {}))["content"]
        except Exception:
            raise RuntimeError("AI_REQUEST_FAILED") from None
        finally:
            conn.close()

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

            return request_json(
                "POST",
                "https://xingchen-api.xf-yun.com/workflow/v1/upload_file",
                files=files,
                headers=self.upload_headers,
            )


if __name__ == "__main__":
    api_key = "20xxxxxxxxxxxx0083741"
    api_secret = "ZjcxxxxxxxxxxxUyNjI2"
    agent = xcAgent(api_key, api_secret)
    inputs = [
        {"key": "AGENT_USER_INPUT", "value": "value1", "type": "string"},
        {"key": "nihao", "value": r"C:\Users\xxxx\Downloads\中环项目运行问题.pdf", "type": "file"},
    ]
    agent.run_astron_flow("735xxxxxxx170", False, inputs)
