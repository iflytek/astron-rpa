import os
import re
import stat
import threading
from pathlib import Path, PureWindowsPath
from typing import Any


class CompressCore:
    @staticmethod
    def _extract_managed_zip(handler, destination):
        """Check streamed bytes independently of ZIP's declared member sizes."""
        root = Path(destination).resolve()
        total = 0
        for item in handler.infolist():
            path = root.joinpath(*item.filename.replace("\\", "/").rstrip("/").split("/"))
            if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path, *path.parents]):
                raise ValueError("Unsafe archive member")
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            size = 0
            with handler.open(item) as source, path.open("wb") as target:
                while chunk := source.read(65536):
                    size += len(chunk)
                    total += len(chunk)
                    if size > 10 * 1024 * 1024 or total > 80 * 1024 * 1024:
                        raise ValueError("Archive exceeds managed file limits")
                    target.write(chunk)

    @staticmethod
    def _extract_managed_7z(handler, destination):
        """Bound actual writes as well as the untrusted archive's size metadata."""
        from py7zr.io import Py7zIO, WriterFactory

        root = Path(destination).resolve()
        writers = []
        total = 0
        lock = threading.Lock()

        class Writer(Py7zIO):
            def __init__(self, path):
                self.stream = path.open("wb+")
                self.length = 0

            def write(self, data):
                nonlocal total
                with lock:
                    end = self.stream.tell() + len(data)
                    if end > 10 * 1024 * 1024 or total + len(data) > 80 * 1024 * 1024:
                        raise ValueError("Archive exceeds managed file limits")
                    total += len(data)
                    self.length = max(self.length, end)
                    return self.stream.write(data)

            def read(self, size=None):
                return self.stream.read(-1 if size is None else size)

            def seek(self, offset, whence=0):
                return self.stream.seek(offset, whence)

            def flush(self):
                self.stream.flush()

            def size(self):
                return self.length

        class Factory(WriterFactory):
            def create(self, filename):
                path = Path(filename)
                if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path, *path.parents]):
                    raise ValueError("Unsafe archive member")
                path.parent.mkdir(parents=True, exist_ok=True)
                writer = Writer(path)
                writers.append(writer)
                return writer

        try:
            for item in handler.list():
                if item.is_directory:
                    root.joinpath(*item.filename.replace("\\", "/").split("/")).mkdir(parents=True, exist_ok=True)
            handler.extractall(path=root, factory=Factory())
        finally:
            for writer in writers:
                writer.stream.close()

    @staticmethod
    def _check_members(members, destination):
        """Reject archive paths/links before writing any member, including on Windows."""
        root = Path(destination).resolve()
        total = 0
        seen = set()
        managed = os.environ.get("ASTRON_RPA_MANAGED_FILES") == "1"
        # Managed files must be portable to Windows. Ordinary extraction keeps
        # the host platform's valid names and case distinctions; the native
        # extractor remains responsible for names the host cannot create.
        windows_names = managed
        for index, (name, size, link) in enumerate(members, 1):
            parts = name.replace("\\", "/").rstrip("/").split("/")
            if (
                link
                or PureWindowsPath(name).is_absolute()
                or not parts
                or any(
                    part in {"", ".", ".."}
                    or "\x00" in part
                    or (
                        windows_names
                        and (
                            re.search(r'[:<>"|?*\x00-\x1f]', part)
                            or part.endswith((".", " "))
                            or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.IGNORECASE)
                        )
                    )
                    for part in parts
                )
            ):
                raise ValueError("Unsafe archive member")
            path = root.joinpath(*parts)
            normalized = str(path).casefold() if windows_names else str(path)
            if normalized in seen or not path.resolve().is_relative_to(root):
                raise ValueError("Unsafe archive member")
            seen.add(normalized)
            if any(p.is_symlink() for p in [path, *path.parents]):
                raise ValueError("Unsafe archive link")
            total += size
            if managed and (index > 512 or size > 10 * 1024 * 1024 or total > 80 * 1024 * 1024):
                raise ValueError("Archive exceeds managed file limits")

    @staticmethod
    def compress(items: list, file_name: str = "", dest_path: str = "", pwd: str = "") -> str:
        import pyzipper

        if not file_name.endswith(".zip"):
            file_name += ".zip"

        try:
            zip_path = os.path.join(dest_path, file_name)
            if pwd:
                with pyzipper.AESZipFile(
                    zip_path,
                    "w",
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES,
                ) as zip_file:
                    zip_file.setpassword(pwd.encode("utf-8"))
                    CompressCore.__add_items_to_zip__(zip_file, items)
            else:
                with pyzipper.ZipFile(zip_path, "w", compression=pyzipper.ZIP_DEFLATED) as zip_file:
                    CompressCore.__add_items_to_zip__(zip_file, items)
            return os.path.abspath(zip_path)
        except Exception as e:
            raise ValueError("压缩失败：{}".format(e))

    @staticmethod
    def __add_items_to_zip__(zip_file, items: list) -> None:
        """
        向zip文件中写入待压缩文件
        """
        for item in items:
            if os.path.isfile(item):
                zip_file.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                folder_name = os.path.basename(item) if len(items) > 1 else ""
                for root, dirs, files in os.walk(item):
                    for file in files:
                        abs_file_path = os.path.join(root, file)
                        relative_file_path = os.path.relpath(abs_file_path, item)
                        zip_file.write(abs_file_path, os.path.join(folder_name, relative_file_path))

    @staticmethod
    def __support_gbk__(zip_file):
        """
        处理ZIP文件中可能存在的中文文件名乱码的问题
        """
        name_to_info = zip_file.NameToInfo
        for name, info in name_to_info.copy().items():
            try:
                real_name = name.encode("cp437").decode("gbk")
            except:
                real_name = name
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
        return zip_file

    @staticmethod
    def uncompress(source_path: str = "", dest_path: str = "", pwd: str = "") -> Any:
        if source_path.endswith(".zip"):
            import pyzipper

            with pyzipper.AESZipFile(source_path) as handler:
                handler = CompressCore.__support_gbk__(handler)
                if pwd:
                    handler.pwd = pwd.encode("utf-8")
                CompressCore._check_members(
                    [
                        (item.filename, item.file_size, stat.S_ISLNK(item.external_attr >> 16))
                        for item in handler.infolist()
                    ],
                    dest_path,
                )
                if os.environ.get("ASTRON_RPA_MANAGED_FILES") == "1":
                    CompressCore._extract_managed_zip(handler, dest_path)
                else:
                    handler.extractall(path=dest_path)
        elif source_path.endswith(".7z"):
            import py7zr

            with py7zr.SevenZipFile(source_path, mode="r", password=pwd) as handler:
                CompressCore._check_members(
                    [
                        (item.filename, item.uncompressed, not (item.is_file or item.is_directory))
                        for item in handler.list()
                    ],
                    dest_path,
                )
                if os.environ.get("ASTRON_RPA_MANAGED_FILES") == "1":
                    CompressCore._extract_managed_7z(handler, dest_path)
                else:
                    handler.extractall(path=dest_path)
        else:
            raise ValueError("不支持的解压缩类型")
        return os.path.abspath(dest_path)
