from unittest.mock import patch
import pytest
from astronverse.openapi.ocr.bank_card import ocr_bank_card


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_bank_card_single(mock_post):
    mock_post.return_value = {"payload": {"card_no": "6222021234567890"}}
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/fake/card.jpg"]):
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda s: s
            mock_file.return_value.__exit__ = lambda s, *args: None
            mock_file.return_value.read.return_value = b"fake_bytes"
            result = ocr_bank_card(src_file="/fake/card.jpg", is_save=False)
    assert len(result) == 1
    mock_post.assert_called_once()


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_bank_card_raises_on_empty_file(mock_post):
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=[]):
        with pytest.raises(Exception):
            ocr_bank_card(src_file="", is_save=False)
