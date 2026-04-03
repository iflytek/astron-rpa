import importlib
import sys
from types import ModuleType, SimpleNamespace


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


def test_encode_imap_utf7_for_chinese_folder_name():
    assert core_imap4_receive.encode_imap_utf7("工作") == b"&XeVPXA-"


def test_decode_folder_list_shows_decoded_folder_name():
    folders = core_imap4_receive.decode_folder_list([b'() "/" "&XeVPXA-"'])

    assert folders == ["'工作'  (raw: &XeVPXA-)"]
