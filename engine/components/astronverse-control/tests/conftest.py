"""控制流组件测试的共享 fixture。

控制流原子能力全部是流程编排标记节点（方法体为 pass），没有可断言的执行行为。
因此测试对准真正被外部消费的契约：注册生成的 meta、locale 文案、config 与 tree 的一致性。
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest
import yaml

LANGS = ("zh_CN", "en_US")


def run_meta_with_diagnostics(work: pathlib.Path) -> None:
    """运行 meta.py，并在原生崩溃时保留足够的定位信息。"""
    command = [sys.executable, "-X", "faulthandler", "-u", "meta.py"]
    result = subprocess.run(
        command,
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return

    unsigned_returncode = result.returncode & 0xFFFFFFFF
    pytest.fail(
        "\n".join(
            [
                "meta.py 执行失败",
                f"returncode: {result.returncode} (0x{unsigned_returncode:08X})",
                f"worker: {os.environ.get('PYTEST_XDIST_WORKER', 'main')}",
                f"python: {sys.executable}",
                f"python_version: {sys.version}",
                f"cwd: {work}",
                f"command: {command!r}",
                f"stdout:\n{result.stdout or '<empty>'}",
                f"stderr:\n{result.stderr or '<empty>'}",
            ]
        ),
        pytrace=False,
    )


@pytest.fixture(scope="session")
def component_dir() -> pathlib.Path:
    """组件根目录（tests/ 的上一级）。"""
    return pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def component_version(component_dir: pathlib.Path) -> str:
    """pyproject.toml 中声明的组件版本。"""
    import tomllib

    data = tomllib.loads((component_dir / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


@pytest.fixture(scope="session")
def config_atomic(component_dir: pathlib.Path) -> dict:
    """config.yaml 的 atomic 区段。"""
    data = yaml.safe_load((component_dir / "config.yaml").read_text(encoding="utf-8"))
    return data["atomic"]


@pytest.fixture(scope="session")
def locales(component_dir: pathlib.Path) -> dict:
    """各语言 locale 文件内容，形如 {lang: locale_dict}。"""
    return {lang: json.loads((component_dir / "locale" / f"{lang}.json").read_text(encoding="utf-8")) for lang in LANGS}


@pytest.fixture(scope="session")
def regenerated(component_dir: pathlib.Path, tmp_path_factory: pytest.TempPathFactory) -> dict:
    """在临时目录重新执行 meta.py，返回生成的产物。

    走子进程而不是直接调用 atomicMg，是因为 atomicMg 与 config 都是全局单例：
    全量跑组件测试时其他组件已经注册进同一个单例，直接断言会互相污染。
    """
    work = tmp_path_factory.mktemp("control-meta")
    for name in ("pyproject.toml", "config.yaml", "meta.py"):
        shutil.copy(component_dir / name, work / name)
    shutil.copytree(component_dir / "locale", work / "locale")

    run_meta_with_diagnostics(work)

    artifacts = {"base": json.loads((work / "meta.json").read_text(encoding="utf-8"))}
    for lang in LANGS:
        artifacts[lang] = {
            "meta": json.loads((work / "resources" / lang / "meta.json").read_text(encoding="utf-8")),
            "tree": json.loads((work / "resources" / lang / "tree.json").read_text(encoding="utf-8")),
        }
    return artifacts


@pytest.fixture(scope="session")
def base_meta(regenerated: dict) -> dict:
    """重新生成的基础 meta（未叠加翻译）。"""
    return regenerated["base"]
