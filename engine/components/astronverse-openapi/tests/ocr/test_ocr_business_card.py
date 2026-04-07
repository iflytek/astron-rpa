from unittest.mock import patch
import pytest
from astronverse.openapi.ocr.business_card import ocr_business_card


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_business_card_single(mock_post):
    mock_post.return_value = {"payload": {"name": "李四"}}
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/fake/bcard.jpg"]):
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda s: s
            mock_file.return_value.__exit__ = lambda s, *args: None
            mock_file.return_value.read.return_value = b"fake_bytes"
            result = ocr_business_card(src_file="/fake/bcard.jpg", is_save=False)
    assert len(result) == 1
    mock_post.assert_called_once()


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_business_card_raises_on_empty_file(mock_post):
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=[]):
        with pytest.raises(Exception):
            ocr_business_card(src_file="", is_save=False)
