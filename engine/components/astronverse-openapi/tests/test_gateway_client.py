import unittest
from unittest.mock import patch, MagicMock
import requests

from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException


class TestGatewayClientMultipart(unittest.TestCase):
    @patch('astronverse.openapi.client.requests.post')
    @patch('astronverse.openapi.client.atomicMg.cfg')
    def test_post_multipart_success(self, mock_cfg, mock_post):
        mock_cfg.return_value.get.return_value = "13159"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        result = GatewayClient.post_multipart("/ocr/general", b"fake_image", "test.jpg", {"lang": "zh"})

        self.assertEqual(result, {"status": "success"})
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args.args[0], "http://127.0.0.1:13159/api/rpa-ai-service/ocr/general")
        self.assertEqual(call_args.kwargs['files'], {"file": ("test.jpg", b"fake_image")})
        self.assertEqual(call_args.kwargs['data'], {"lang": "zh"})

    @patch('astronverse.openapi.client.requests.post')
    @patch('astronverse.openapi.client.atomicMg.cfg')
    def test_post_multipart_raises_domain_error_on_http_failure(self, mock_cfg, mock_post):
        mock_cfg.return_value.get.return_value = "13159"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "gateway failed"
        mock_post.return_value = mock_response

        with self.assertRaises(BizException) as exc_info:
            GatewayClient.post_multipart("/ocr/general", b"fake_image", "test.jpg", {"lang": "zh"})

        self.assertIn("ai服务器无响应或错误", str(exc_info.exception))
        self.assertIn("gateway failed", exc_info.exception.message)

    @patch('astronverse.openapi.client.requests.request')
    @patch('astronverse.openapi.client.atomicMg.cfg')
    def test_post_raises_domain_error_on_request_exception(self, mock_cfg, mock_request):
        mock_cfg.return_value.get.return_value = "13159"
        mock_request.side_effect = requests.RequestException("connection reset")

        with self.assertRaises(BizException) as exc_info:
            GatewayClient.post("/ocr/document", {"image": "abc"})

        self.assertIn("ai服务请求异常", str(exc_info.exception))
        self.assertIn("connection reset", exc_info.exception.message)
