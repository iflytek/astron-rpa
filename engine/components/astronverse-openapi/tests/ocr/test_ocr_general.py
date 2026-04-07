from unittest.mock import patch
import pytest
from astronverse.openapi.error import BizException
from astronverse.openapi.ocr.general import ocr_general


@patch("astronverse.openapi.ocr.general.GatewayClient.post")
def test_ocr_general_single(mock_post):
    mock_post.return_value = {"payload": {"words": "测试文字"}}
    with patch("astronverse.openapi.ocr.general.utils.generate_src_files", return_value=["/fake/image.jpg"]):
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda s: s
            mock_file.return_value.__exit__ = lambda s, *args: None
            mock_file.return_value.read.return_value = b"fake_bytes"
            result = ocr_general(src_file="/fake/image.jpg", is_save=False)
    assert len(result) == 1
    mock_post.assert_called_once()


@patch("astronverse.openapi.ocr.general.GatewayClient.post")
def test_ocr_general_raises_on_empty_file(mock_post):
    with patch("astronverse.openapi.ocr.general.utils.generate_src_files", return_value=[]):
        with pytest.raises(BizException) as exc_info:
            ocr_general(src_file="", is_save=False)
    assert "图像路径不存在或格式错误" in str(exc_info.value)
