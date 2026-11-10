import pytest
from astronverse.scheduler.config import Config
from astronverse.scheduler.utils.validators import (
    validate_mirror,
    validate_package_name,
    validate_project_id,
    validate_version,
)


@pytest.mark.parametrize("name", ["requests", "pywin32", "zope.interface", "typing_extensions", "a", "PyYAML"])
def test_valid_package_names(name):
    assert validate_package_name(name) == name


@pytest.mark.parametrize(
    "name",
    [
        "",
        "git+https://evil.example/x.git",
        "https://evil.example/x.tar.gz",
        "../x",
        "./local_dir",
        "-r requirements.txt",
        "--index-url=https://evil.example",
        "pkg @ http://evil.example/x.whl",
        "pkg[extra]",
        "a'b",
        "pkg;os_name=='nt'",
        "pkg==1.0",
    ],
)
def test_invalid_package_names(name):
    with pytest.raises(ValueError):
        validate_package_name(name)


@pytest.mark.parametrize("ver", ["", "1.0", "2.31.0", "1.0rc1", "1!2.0", "1.0+local", "1.0.post1"])
def test_valid_versions(ver):
    assert validate_version(ver) == ver


@pytest.mark.parametrize("ver", ["1.0 @ http://x", "1.0;x", "-1.0", "1.0 --index-url=x", "' or 1"])
def test_invalid_versions(ver):
    with pytest.raises(ValueError):
        validate_version(ver)


@pytest.mark.parametrize(
    "mirror",
    [
        "https://pypi.mirrors.ustc.edu.cn/simple/",
        "https://mirrors.aliyun.com/pypi/simple",
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://pypi.python.org/simple",
        "http://pypi.douban.com/simple/",
    ],
)
def test_valid_mirrors(mirror):
    assert validate_mirror(mirror) == mirror


@pytest.mark.parametrize(
    "mirror",
    [
        "",
        "https://evil.example/simple",
        "https://mirrors.aliyun.com.evil.example/simple",
        "file:///C:/pkgs",
        "ftp://mirrors.aliyun.com/pypi",
        "https://user:pass@mirrors.aliyun.com/pypi/simple",
    ],
)
def test_invalid_mirrors(mirror):
    with pytest.raises(ValueError):
        validate_mirror(mirror)


def test_extra_mirror_hosts_from_config(monkeypatch):
    monkeypatch.setattr(Config, "pip_mirror_allow_hosts", ["pypi.internal.corp"])
    assert validate_mirror("https://pypi.internal.corp/simple")


@pytest.mark.parametrize("project_id", ["1234567890", "abc_DEF-123"])
def test_valid_project_ids(project_id):
    assert validate_project_id(project_id) == project_id


@pytest.mark.parametrize("project_id", ["", "..", "../x", "a/b", "a\\b", "C:", None, "x" * 65])
def test_invalid_project_ids(project_id):
    with pytest.raises(ValueError):
        validate_project_id(project_id)
