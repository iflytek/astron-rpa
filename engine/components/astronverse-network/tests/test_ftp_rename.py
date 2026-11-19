from unittest.mock import Mock

import pytest
from astronverse.network import FileExistenceType, FileType
from astronverse.network.core_ftp import FtpCore
from astronverse.network.ftp import FTP


@pytest.mark.parametrize("stale_file_name", ["", "unrelated.txt"])
@pytest.mark.parametrize(
    ("existing", "policy", "expected"),
    [
        (False, FileExistenceType.RENAME, "new_folder"),
        (True, FileExistenceType.CANCEL, "old_folder"),
        (True, FileExistenceType.OVERWRITE, "new_folder"),
        (True, FileExistenceType.RENAME, "new_folder_1"),
    ],
)
def test_folder_rename_uses_folder_source(monkeypatch, stale_file_name, existing, policy, expected):
    client = Mock()
    client.nlst.return_value = ["old_folder"] + (["new_folder"] if existing else [])
    client.pwd.return_value = "/home"
    monkeypatch.setattr(FtpCore, "is_dir", lambda connection, name: name == "old_folder")
    delete = Mock()
    monkeypatch.setattr(FtpCore, "ftp_delete_dir", delete)
    monkeypatch.setattr(FtpCore, "generate_name", lambda connection, name: name + "_1")
    rename = getattr(FTP.ftp_rename, "__wrapped__", FTP.ftp_rename)

    result = rename(
        client,
        file_type=FileType.FOLDER,
        cur_file_name=stale_file_name,
        cur_folder_name="old_folder",
        new_folder_name="new_folder",
        exist_type=policy,
    )

    assert result.replace("\\", "/") == "/home/" + expected
    if existing and policy == FileExistenceType.CANCEL:
        client.rename.assert_not_called()
    else:
        client.rename.assert_called_once_with("old_folder", expected)
    if existing and policy == FileExistenceType.OVERWRITE:
        delete.assert_called_once_with(client, "new_folder")
    else:
        delete.assert_not_called()


def test_file_rename_preserves_extension():
    client = Mock()
    client.nlst.return_value = ["old.txt"]
    client.pwd.return_value = "/home"
    rename = getattr(FTP.ftp_rename, "__wrapped__", FTP.ftp_rename)
    result = rename(client, cur_file_name="old.txt", new_file_name="new")
    client.rename.assert_called_once_with("old.txt", "new.txt")
    assert result.replace("\\", "/") == "/home/new.txt"
