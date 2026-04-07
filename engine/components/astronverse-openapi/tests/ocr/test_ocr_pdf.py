from unittest.mock import patch
import pytest
from astronverse.openapi.error import BizException
from astronverse.openapi.ocr.pdf import ocr_pdf


@patch("astronverse.openapi.ocr.pdf.GatewayClient.post")
def test_ocr_pdf_with_url(mock_post):
    mock_post.return_value = {
        "payload": {"task_no": "T001", "status": "done", "page_count": 5, "result_url": "http://x.com/r"}
    }
    result = ocr_pdf(pdf_url="http://example.com/test.pdf")
    assert result["task_no"] == "T001"
    assert result["page_count"] == 5


def test_ocr_pdf_raises_when_no_input():
    with pytest.raises(BizException) as exc_info:
        ocr_pdf()
    assert "图片路径不存在或格式错误" in str(exc_info.value)
