from unittest.mock import Mock

import pytest
from astronverse.excel.core_win import application


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


def test_managed_excel_uses_private_instance_disables_macros_and_link_updates(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    app = Mock(AutomationSecurity=0)
    app.Workbooks.Count = 0
    isolated, shared = Mock(return_value=app), Mock()
    monkeypatch.setattr(application.win32com.client, "DispatchEx", isolated)
    monkeypatch.setattr(application.win32com.client, "Dispatch", shared)
    assert application._create_app("Ket.Application") is app
    assert app.AutomationSecurity == 3
    assert app.AskToUpdateLinks is False
    shared.assert_not_called()
    monkeypatch.setattr(application, "ExcelObj", lambda **kwargs: kwargs)
    application.Application.open_workbook(app, "test.xlsx", update_links=True)
    assert app.Workbooks.Open.call_args.kwargs["UpdateLinks"] is False


def test_missing_alias_allows_next_office_provider(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    monkeypatch.setattr(application.win32com.client, "DispatchEx", Mock(side_effect=OSError()))
    assert application._create_app("Excel.Application") is None


def test_legacy_workbook_keeps_explicit_link_option(monkeypatch):
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES", raising=False)
    app = Mock()
    monkeypatch.setattr(application, "ExcelObj", lambda **kwargs: kwargs)
    application.Application.open_workbook(app, "test.xlsx", update_links=True)
    assert app.Workbooks.Open.call_args.kwargs["UpdateLinks"] is True


def test_macro_security_failure_is_not_ignored(monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")

    class UnsafeOffice:
        AutomationSecurity = property(lambda _: 1, lambda *_: None)
        Quit = Mock()
        Workbooks = Mock(Count=0)
        Hwnd = 10

    app = UnsafeOffice()
    monkeypatch.setattr(application.win32com.client, "DispatchEx", lambda _: app)
    with pytest.raises(RuntimeError):
        application._create_app("Ket.Application")
    app.Quit.assert_called_once()


def test_existing_office_process_is_never_registered_or_closed(monkeypatch, tmp_path):
    import psutil

    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    directory = tmp_path / "execution.files"
    directory.mkdir()
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES_DIRECTORY", str(directory))
    monkeypatch.setattr(psutil, "pids", lambda: [2])
    app = Mock(AutomationSecurity=0)
    app.Workbooks.Count = 0
    monkeypatch.setattr(application.win32com.client, "DispatchEx", lambda _: app)
    with pytest.raises(RuntimeError, match="existing process"):
        application._create_app("Ket.Application")
    app.Quit.assert_not_called()
    assert list(directory.iterdir()) == []


def test_private_office_process_identity_is_persisted(monkeypatch, tmp_path):
    import json

    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    directory = tmp_path / "execution.files"
    directory.mkdir()
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES_DIRECTORY", str(directory))
    app = Mock(AutomationSecurity=0)
    app.Workbooks.Count = 0
    monkeypatch.setattr(application.win32com.client, "DispatchEx", lambda _: app)
    application._create_app("Ket.Application")
    assert json.loads((directory / "office-2.json").read_text()) == {"pid": 2, "created": 1.0}
