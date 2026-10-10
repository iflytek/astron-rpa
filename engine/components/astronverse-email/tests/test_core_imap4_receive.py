import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock


def _install_logger_stub():
    baseline_module = ModuleType("astronverse.baseline")
    baseline_logger_module = ModuleType("astronverse.baseline.logger")
    logger_module = ModuleType("astronverse.baseline.logger.logger")
    logger_module.logger = SimpleNamespace(info=lambda *args, **kwargs: None)

    sys.modules["astronverse.baseline"] = baseline_module
    sys.modules["astronverse.baseline.logger"] = baseline_logger_module
    sys.modules["astronverse.baseline.logger.logger"] = logger_module


_install_logger_stub()
core_imap4_receive = importlib.import_module("astronverse.email.core_imap4_receive")


def test_read_session_uses_examine_and_peek_without_store_or_expunge():
    core = core_imap4_receive.EmailImap4Receive()
    handler = core.mail_handler = Mock()
    handler.list.return_value = ("OK", [b'() "/" "INBOX"'])
    handler.fetch.return_value = ("OK", [(b"1", b"Subject: test\r\n\r\nbody")])
    core.select("INBOX", readonly=True)
    result = core.get_entire_mail_info(b"1")
    assert result["subject"] == "test"
    handler.select.assert_called_once_with(b"INBOX", readonly=True)
    handler.fetch.assert_called_once_with(b"1", "(BODY.PEEK[])")
    core.logout()
    handler.logout.assert_called_once()
    handler.store.assert_not_called()
    handler.close.assert_not_called()
    assert core.mail_handler is None


def test_encode_imap_utf7_for_chinese_folder_name():
    assert core_imap4_receive.encode_imap_utf7("工作") == b"&XeVPXA-"


def test_decode_folder_list_shows_decoded_folder_name():
    folders = core_imap4_receive.decode_folder_list([b'() "/" "&XeVPXA-"'])

    assert folders == ["'工作'  (raw: &XeVPXA-)"]
