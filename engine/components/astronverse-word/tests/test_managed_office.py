from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from astronverse.word import SaveFileType, core_win


def test_convert_to_txt_reads_open_document_paragraphs(tmp_path):
    # No FullName: an unsaved document must not be reopened from disk.
    document = SimpleNamespace(
        Paragraphs=[
            SimpleNamespace(Range=SimpleNamespace(Text=text))
            for text in ["中文 paragraph\r", "\r", "cell\r\a", "trailing spaces  \r"]
        ]
    )
    core_win.WordDocumentCore.convert_to_txt(document, str(tmp_path), "output")
    assert (tmp_path / "output.txt").read_text(encoding="utf-8") == ("中文 paragraph\n\ncell\ntrailing spaces  \n")


@pytest.mark.parametrize("policy", [SaveFileType.WARN, SaveFileType.GENERATE, SaveFileType.OVERWRITE])
def test_convert_to_txt_preserves_collision_policy(tmp_path, policy):
    destination = tmp_path / "output.txt"
    destination.write_text("original", encoding="utf-8")
    (tmp_path / "output_1.txt").write_text("previous copy", encoding="utf-8")
    document = SimpleNamespace(Paragraphs=[SimpleNamespace(Range=SimpleNamespace(Text="new\r"))])

    if policy == SaveFileType.WARN:
        with pytest.raises(core_win.BaseException):
            core_win.WordDocumentCore.convert_to_txt(document, str(tmp_path), "output", policy)
        assert destination.read_text(encoding="utf-8") == "original"
        assert not (tmp_path / "output_2.txt").exists()
    else:
        core_win.WordDocumentCore.convert_to_txt(document, str(tmp_path), "output", policy)
        target = tmp_path / "output_2.txt" if policy == SaveFileType.GENERATE else destination
        assert target.read_text(encoding="utf-8") == "new\n"
        if policy == SaveFileType.GENERATE:
            assert destination.read_text(encoding="utf-8") == "original"
    assert (tmp_path / "output_1.txt").read_text(encoding="utf-8") == "previous copy"


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
