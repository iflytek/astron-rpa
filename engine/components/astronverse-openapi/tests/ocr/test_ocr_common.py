import os
from unittest.mock import patch, mock_open, MagicMock
import pytest
from astronverse.openapi.ocr._common import _read_image_bytes, _collect_dir_files, _run_multipart_ocr


def test_read_image_bytes_returns_filename_and_bytes():
    m = mock_open(read_data=b"fake_bytes")
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/tmp/test.jpg"]):
        with patch("builtins.open", m):
            fname, fbytes = _read_image_bytes("/tmp/test.jpg")
            assert fname == "test.jpg"
            assert fbytes == b"fake_bytes"


def test_read_image_bytes_raises_on_empty():
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=[]):
        with pytest.raises(Exception):
            _read_image_bytes("")


def test_collect_dir_files_returns_files():
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/tmp/a.jpg", "/tmp/b.jpg"]):
        files = _collect_dir_files("/tmp/images")
        assert len(files) == 2


def test_collect_dir_files_raises_on_empty():
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=[]):
        with pytest.raises(Exception):
            _collect_dir_files("/tmp/empty")


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_run_multipart_ocr_single(mock_post):
    mock_post.return_value = {"payload": {"words": "test"}}
    m = mock_open(read_data=b"fake_bytes")
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/tmp/test.jpg"]):
        with patch("builtins.open", m):
            results = _run_multipart_ocr("/ocr/general", False, "/tmp/test.jpg", "", False, "", "")
    assert len(results) == 1
    mock_post.assert_called_once()
