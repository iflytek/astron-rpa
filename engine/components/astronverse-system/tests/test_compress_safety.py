import io
import os
import stat
import zipfile
from types import SimpleNamespace

import py7zr
import pytest
from astronverse.system.core.compress_core import CompressCore


@pytest.mark.parametrize("name", ["../escape.txt", "..\\escape.txt", "/absolute", "C:/outside", "x/../../escape"])
def test_archive_traversal_rejected_before_extraction(tmp_path, name):
    source = tmp_path / "bad.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("normal.txt", "safe")
        archive.writestr(name, "unsafe")
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Unsafe archive"):
        CompressCore.uncompress(str(source), str(output))
    assert not output.exists()


def test_archive_links_are_rejected(tmp_path):
    source = tmp_path / "link.zip"
    with zipfile.ZipFile(source, "w") as archive:
        link = zipfile.ZipInfo("link")
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(link, "../outside")
    with pytest.raises(ValueError):
        CompressCore.uncompress(str(source), str(tmp_path / "out"))


@pytest.mark.parametrize("extension", ["zip", "7z"])
def test_managed_archive_roundtrip(tmp_path, monkeypatch, extension):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    source = tmp_path / ("valid." + extension)
    payload = tmp_path / "sample.txt"
    payload.write_bytes(b"sample")
    if extension == "zip":
        with zipfile.ZipFile(source, "w") as archive:
            archive.write(payload, "nested/sample.txt")
    else:
        with py7zr.SevenZipFile(source, "w") as archive:
            archive.write(payload, "nested/sample.txt")
    output = tmp_path / "output"
    CompressCore.uncompress(str(source), str(output))
    assert (output / "nested/sample.txt").read_bytes() == b"sample"


def test_managed_archive_resource_bounds_preserve_legacy_size_behavior(tmp_path, monkeypatch):
    members = [("large.txt", 10 * 1024 * 1024 + 1, False)]
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES", raising=False)
    CompressCore._check_members(members, tmp_path)
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    with pytest.raises(ValueError, match="limits"):
        CompressCore._check_members(members, tmp_path)
    with pytest.raises(ValueError, match="limits"):
        CompressCore._check_members([(f"{i}.txt", 1, False) for i in range(513)], tmp_path)


def test_managed_7z_enforces_actual_write_budget(tmp_path):
    class UnderreportedArchive:
        def list(self):
            return []

        def extractall(self, path, factory):
            writer = factory.create(str(path / "large.txt"))
            writer.write(b"x" * (10 * 1024 * 1024 + 1))

    with pytest.raises(ValueError, match="limits"):
        CompressCore._extract_managed_7z(UnderreportedArchive(), tmp_path)
    assert (tmp_path / "large.txt").stat().st_size == 0


@pytest.mark.skipif(os.name == "nt", reason="POSIX names are not valid Windows filenames")
def test_unmanaged_zip_preserves_posix_names_and_case(tmp_path, monkeypatch):
    source = tmp_path / "posix.zip"
    with zipfile.ZipFile(source, "w") as archive:
        for name in ("report:v2.txt", "CON.log", "File.txt", "file.txt"):
            archive.writestr(name, name)
    output = tmp_path / "output"
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES", raising=False)
    CompressCore.uncompress(str(source), str(output))
    assert {(path.name, path.read_text()) for path in output.iterdir()} == {
        ("report:v2.txt", "report:v2.txt"),
        ("CON.log", "CON.log"),
        ("File.txt", "File.txt"),
        ("file.txt", "file.txt"),
    }


def test_unmanaged_member_rules_do_not_apply_windows_aliases(tmp_path, monkeypatch):
    monkeypatch.delenv("ASTRON_RPA_MANAGED_FILES", raising=False)
    CompressCore._check_members(
        [(name, 1, False) for name in ("report:v2.txt", "CON.log", "File.txt", "file.txt")],
        tmp_path,
    )


def test_managed_zip_enforces_windows_names_and_actual_write_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("ASTRON_RPA_MANAGED_FILES", "1")
    with pytest.raises(ValueError, match="Unsafe archive"):
        CompressCore._check_members([("report:v2.txt", 1, False)], tmp_path)
    with pytest.raises(ValueError, match="Unsafe archive"):
        CompressCore._check_members([("NUL", 1, False)], tmp_path)
    with pytest.raises(ValueError, match="Unsafe archive"):
        CompressCore._check_members([("File.txt", 1, False), ("file.txt", 1, False)], tmp_path)

    class UnderreportedArchive:
        def infolist(self):
            return [SimpleNamespace(filename="large.txt", file_size=0, is_dir=lambda: False)]

        def open(self, _item):
            return io.BytesIO(b"x" * (10 * 1024 * 1024 + 1))

    with pytest.raises(ValueError, match="limits"):
        CompressCore._extract_managed_zip(UnderreportedArchive(), tmp_path / "zip-output")
