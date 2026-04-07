import base64
import json
from unittest.mock import patch
from astronverse.openapi.ocr.document import ocr_document


@patch("astronverse.openapi.ocr.document.GatewayClient.post")
def test_ocr_document_parses_base64(mock_post):
    raw = {"text": "识别内容", "pages": 1}
    encoded = base64.b64encode(json.dumps(raw).encode()).decode()
    mock_post.return_value = {"payload": {"result": {"text": encoded}}}

    with patch("astronverse.openapi.ocr.document.utils.generate_src_files", return_value=["/fake/doc.jpg"]):
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda s: s
            mock_file.return_value.__exit__ = lambda s, *args: None
            mock_file.return_value.read.return_value = b"fake_image"
            result = ocr_document(src_file="/fake/doc.jpg", is_save=False)

    assert result["text"] == "识别内容"
    assert result["raw"]["pages"] == 1
    assert result["saved_file"] == ""
