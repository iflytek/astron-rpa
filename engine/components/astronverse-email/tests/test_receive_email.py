import importlib
import sys
from enum import Enum
from types import ModuleType, SimpleNamespace

import pytest


class _AtomicFormType(Enum):
    CONTENTPASTE = "contentpaste"
    INPUT_VARIABLE_PYTHON_FILE = "input_variable_python_file"
    MODALBUTTON = "modalbutton"
    CHECKBOX = "checkbox"


class _AtomicLevel(Enum):
    NORMAL = "normal"


class _AtomicFormTypeMeta:
    def __init__(self, type, params=None):
        self.type = type
        self.params = params or {}


class _DynamicsItem:
    def __init__(self, key, expression):
        self.key = key
        self.expression = expression


def _install_email_module_stubs():
    actionlib_module = ModuleType("astronverse.actionlib")
    actionlib_module.AtomicFormType = _AtomicFormType
    actionlib_module.AtomicFormTypeMeta = _AtomicFormTypeMeta
    actionlib_module.AtomicLevel = _AtomicLevel
    actionlib_module.DynamicsItem = _DynamicsItem

    atomic_module = ModuleType("astronverse.actionlib.atomic")
    atomic_module.atomicMg = SimpleNamespace(
        atomic=lambda *args, **kwargs: (lambda func: func),
        param=lambda *args, **kwargs: {"args": args, "kwargs": kwargs},
    )

    baseline_module = ModuleType("astronverse.baseline")
    baseline_logger_module = ModuleType("astronverse.baseline.logger")
    logger_module = ModuleType("astronverse.baseline.logger.logger")
    logger_module.logger = SimpleNamespace(info=lambda *args, **kwargs: None)

    sys.modules["astronverse.actionlib"] = actionlib_module
    sys.modules["astronverse.actionlib.atomic"] = atomic_module
    sys.modules["astronverse.baseline"] = baseline_module
    sys.modules["astronverse.baseline.logger"] = baseline_logger_module
    sys.modules["astronverse.baseline.logger.logger"] = logger_module


_install_email_module_stubs()
from astronverse.email import EmailServerType, core_imap4_receive

Email = importlib.import_module("astronverse.email.email").Email


class FakeEmailImap4Receive:
    instances = []

    def __init__(self):
        self.instances.append(self)
        self.logged_out = False
        self.masked_mail_id = None

    def login(self, server, port, user, password):
        self.login_args = {
            "server": server,
            "port": port,
            "user": user,
            "password": password,
        }

    def select(self, selector, readonly=False):
        self.selected_folder = selector
        self.readonly = readonly

    def logout(self):
        self.logged_out = True

    def search(self, charset="utf-8", *criteria):
        return "OK", [b"1 2 3 4"]

    def get_entire_mail_info(self, num):
        mail_id = num.decode() if isinstance(num, bytes) else str(num)
        mail_times = {
            "1": "2026-03-11 00:00:00",
            "2": "2026-03-08 00:00:00",
            "3": "2026-03-10 00:00:00",
            "4": "2026-03-09 00:00:00",
        }
        return {
            "from": ("sender", "sender@example.com"),
            "to": ("receiver", "receiver@example.com"),
            "subject": f"subject-{mail_id}",
            "body": f"body-{mail_id}",
            "html": None,
            "time": mail_times[mail_id],
            "attachments": [],
        }

    def mask_as_read(self, num):
        self.masked_mail_id = num


def test_receive_email_returns_latest_messages_first(monkeypatch):
    monkeypatch.setattr(core_imap4_receive, "EmailImap4Receive", FakeEmailImap4Receive)

    result = Email.receive_email(
        mail_server=EmailServerType.QQ,
        user_mail="user@example.com",
        user_password="password",
        max_return_num=2,
        folder_name="INBOX",
    )

    assert [item["subject"] for item in result] == ["subject-1", "subject-3"]
    assert result[0]["from"] == ["sender", "sender@example.com"]
    assert result[0]["to"] == ["receiver", "receiver@example.com"]
    core = FakeEmailImap4Receive.instances[-1]
    assert core.readonly is True
    assert core.logged_out is True
    assert core.masked_mail_id is None


def test_mark_read_remains_explicit_and_session_is_released(monkeypatch):
    monkeypatch.setattr(core_imap4_receive, "EmailImap4Receive", FakeEmailImap4Receive)
    Email.receive_email(mask_as_read_flag=True, max_return_num=1)
    core = FakeEmailImap4Receive.instances[-1]
    assert core.readonly is False
    assert core.masked_mail_id == b"1"
    assert core.logged_out is True


def test_search_failure_still_releases_session(monkeypatch):
    def fail(*args):
        raise RuntimeError("search failed")

    monkeypatch.setattr(core_imap4_receive, "EmailImap4Receive", FakeEmailImap4Receive)
    monkeypatch.setattr(FakeEmailImap4Receive, "search", fail)
    with pytest.raises(RuntimeError):
        Email.receive_email()
    assert FakeEmailImap4Receive.instances[-1].logged_out is True
