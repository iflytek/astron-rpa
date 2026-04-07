from pathlib import Path
from unittest.mock import patch

from astronverse.openapi.error import BizException
from astronverse.openapi.nlp.translate import nlp_translate


@patch("astronverse.openapi.nlp.translate.GatewayClient.post")
def test_nlp_translate_exports_txt_with_translated_text(mock_post, tmp_path):
    mock_post.return_value = {
        "header": {"code": 0, "message": "success", "sid": "sid"},
        "decoded_result": {
            "from": "cn",
            "to": "en",
            "trans_result": {
                "src": "你好",
                "dst": "Hello",
            },
        },
    }

    result = nlp_translate(
        input_type="text",
        text="你好",
        from_lang="cn",
        to_lang="en",
        is_save=True,
        dst_file=str(tmp_path),
        dst_file_name="text_translation",
    )

    saved_file = Path(result["saved_file"])

    assert saved_file.exists()
    assert saved_file.read_text(encoding="utf-8") == "Hello"
    mock_post.assert_called_once_with(
        "/nlp/translate",
        {"text": "你好", "from": "cn", "to": "en"},
    )


def test_nlp_translate_rejects_same_languages():
    try:
        nlp_translate(
            input_type="text",
            text="你好",
            from_lang="en",
            to_lang="en",
        )
    except BizException as exc:
        assert "二者不可一致，请重新选择" in str(exc)
    else:
        raise AssertionError("Expected same-language validation to fail")
