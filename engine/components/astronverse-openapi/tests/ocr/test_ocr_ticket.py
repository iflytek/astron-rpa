from unittest.mock import patch
from astronverse.openapi.ocr.ticket import ocr_ticket


@patch("astronverse.openapi.ocr._common.GatewayClient.post_multipart")
def test_ocr_ticket_train(mock_post):
    mock_post.return_value = {"payload": {"ticket_no": "G1234"}}
    with patch("astronverse.openapi.ocr._common.utils.generate_src_files", return_value=["/fake/ticket.jpg"]):
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__ = lambda s: s
            mock_file.return_value.__exit__ = lambda s, *args: None
            mock_file.return_value.read.return_value = b"fake_bytes"
            result = ocr_ticket(ticket_type="train_ticket", src_file="/fake/ticket.jpg", is_save=False)
    assert len(result) == 1
    call_args = mock_post.call_args
    assert call_args.args[3]["ocr_type"] == "train_ticket"
