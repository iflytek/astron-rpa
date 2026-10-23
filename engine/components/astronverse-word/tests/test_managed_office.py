from unittest.mock import Mock

import pytest
from astronverse.word import core_win


@pytest.fixture(autouse=True)
def private_process(monkeypatch):
    import psutil
    import win32process
    from astronverse.actionlib import managed_office

    monkeypatch.setattr(psutil, "pids", lambda: [])
    monkeypatch.setattr(psutil, "Process", Mock(return_value=Mock(create_time=lambda: 1.0)))
    monkeypatch.setattr(win32process, "GetWindowThreadProcessId", lambda _: (1, 2))
    monkeypatch.setattr(managed_office, "register", lambda _: None)
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES_DIRECTORY", raising=False)


def test_managed_word_uses_private_instance_and_disables_macros(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    app = Mock(AutomationSecurity=0)
    app.Documents.Count = 0
    private, shared = Mock(return_value=app), Mock()
    monkeypatch.setattr(core_win.wc, "DispatchEx", private)
    monkeypatch.setattr(core_win.wc.gencache, "EnsureDispatch", shared)
    assert core_win.WordDocumentCore._create_word_application("Kwps.Application") is app
    assert app.AutomationSecurity == 3
    shared.assert_not_called()


def test_missing_word_alias_allows_next_office_provider(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    monkeypatch.setattr(core_win.wc, "DispatchEx", Mock(side_effect=OSError()))
    assert core_win.WordDocumentCore._create_word_application("Word.Application") is None


def test_legacy_word_keeps_existing_dispatch_behavior(monkeypatch):
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES", raising=False)
    app = Mock()
    monkeypatch.setattr(core_win.wc.gencache, "EnsureDispatch", Mock(return_value=app))
    isolated = Mock()
    monkeypatch.setattr(core_win.wc, "DispatchEx", isolated)
    assert core_win.WordDocumentCore._create_word_application("Word.Application") is app
    isolated.assert_not_called()


def test_word_macro_security_failure_is_not_ignored(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")

    class UnsafeOffice:
        AutomationSecurity = property(lambda _: 1, lambda *_: None)
        Quit = Mock()
        Documents = Mock(Count=0)

    app = UnsafeOffice()
    monkeypatch.setattr(core_win.wc, "DispatchEx", lambda _: app)
    with pytest.raises(RuntimeError):
        core_win.WordDocumentCore._create_word_application("Kwps.Application")
    app.Documents.Add.assert_not_called()
    app.Quit.assert_not_called()  # No proven process identity; never close a user's instance.
