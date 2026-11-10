from unittest.mock import MagicMock

import pytest
from astronverse.scheduler.utils import pip as pip_module
from astronverse.scheduler.utils.pip import PipManager


def test_download_cmd_uses_tls_for_https_mirror():
    cmd = PipManager.download_pip_cmd("requests", "2.31.0", "https://mirrors.aliyun.com/pypi/simple", "python")
    assert "requests==2.31.0" in cmd
    assert "--index-url=https://mirrors.aliyun.com/pypi/simple" in cmd
    assert "--trusted-host" not in cmd


def test_download_cmd_keeps_trusted_host_for_http_mirror():
    cmd = PipManager.download_pip_cmd("requests", "", "http://pypi.douban.com/simple/", "python")
    index = cmd.index("--trusted-host")
    assert cmd[index + 1] == "pypi.douban.com"


@pytest.mark.parametrize(
    ("package", "ver", "mirror"),
    [
        ("git+https://evil.example/x.git", "", "https://mirrors.aliyun.com/pypi/simple"),
        ("requests", "1.0 @ http://evil.example", "https://mirrors.aliyun.com/pypi/simple"),
        ("requests", "", "https://evil.example/simple"),
    ],
)
def test_download_cmd_rejects_untrusted_input(package, ver, mirror):
    with pytest.raises(ValueError):
        PipManager.download_pip_cmd(package, ver, mirror, "python")


def test_install_cmd_rejects_invalid_package():
    with pytest.raises(ValueError):
        PipManager.install_pip_cmd("../evil", "", "python")


def test_package_version_passes_name_as_argument(monkeypatch):
    captured = {}

    def fake_sub_popen(cmd):
        captured["cmd"] = cmd
        proc = MagicMock()
        proc.run.return_value.proc.communicate.return_value = ("1.0\n", "")
        return proc

    monkeypatch.setattr(pip_module, "SubPopen", fake_sub_popen)
    assert PipManager.package_version("requests", exec_python="python") == "1.0"
    assert captured["cmd"][-1] == "requests"
    assert "requests" not in captured["cmd"][2]


def test_package_version_rejects_code_injection():
    with pytest.raises(ValueError):
        PipManager.package_version("x'); import os; os.system('calc'); ('", exec_python="python")
