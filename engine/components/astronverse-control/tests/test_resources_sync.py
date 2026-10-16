"""已提交的 resources/ 产物与重新生成结果的一致性测试。

resources/ 下的 meta.json / tree.json 是随包分发、被前端直接读取的产物，但由
`uv run meta.py` 手动生成。改了 control.py、locale 或 config.yaml 却忘记重新生成，
运行期就会读到旧的原子定义。此处用重新生成的结果比对已提交文件来拦住这种漂移。

注意：这些产物在组件 .gitignore 中被忽略，干净检出（CI）下并不存在。产物缺失时
本文件的漂移比对无参照物，统一 skip；产物存在时（本地跑过 meta.py）才做比对。
不依赖已提交产物的结构与确定性断言不受影响，始终执行。
"""

import json
import pathlib

import pytest

LANGS = ("zh_CN", "en_US")


def _read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_committed(path: pathlib.Path) -> dict:
    """Read a generated artifact, skipping the test when it has not been generated."""
    if not path.is_file():
        pytest.skip(f"generated artifact missing, run `uv run meta.py` first: {path}")
    return _read_json(path)


def test_committed_base_meta_is_up_to_date(component_dir, base_meta):
    """meta.json 必须与当前 control.py + config.yaml 反射出的结果一致。"""
    assert _read_committed(component_dir / "meta.json") == base_meta


@pytest.mark.parametrize("lang", LANGS)
def test_committed_locale_meta_is_up_to_date(component_dir, regenerated, lang):
    """resources/{lang}/meta.json 必须与叠加当前 locale 后的结果一致。"""
    committed = _read_committed(component_dir / "resources" / lang / "meta.json")
    assert committed == regenerated[lang]["meta"]


@pytest.mark.parametrize("lang", LANGS)
def test_committed_tree_is_up_to_date(component_dir, regenerated, lang):
    """resources/{lang}/tree.json 必须与当前 config.yaml 构建出的树一致。"""
    committed = _read_committed(component_dir / "resources" / lang / "tree.json")
    assert committed == regenerated[lang]["tree"]


@pytest.mark.parametrize("lang", LANGS)
def test_resources_exist_for_every_language(component_dir, lang):
    """产物一旦生成，两种语言都要齐全，缺一种前端切换语言会拿不到 meta。"""
    if not (component_dir / "resources").is_dir():
        pytest.skip("resources/ not generated, run `uv run meta.py` first")
    for name in ("meta.json", "tree.json"):
        assert (component_dir / "resources" / lang / name).is_file()


@pytest.mark.parametrize("lang", LANGS)
def test_locale_resources_keep_same_atomic_set(regenerated, base_meta, lang):
    """叠加翻译不应增删原子能力，只替换文案。"""
    assert set(regenerated[lang]["meta"]) == set(base_meta)


@pytest.mark.parametrize("lang", LANGS)
def test_locale_resources_preserve_param_structure(regenerated, base_meta, lang):
    """翻译不得改动参数 key、顺序、types 与 options 的 value。"""
    translated_meta = regenerated[lang]["meta"]
    for key, atomic in base_meta.items():
        for list_key in ("inputList", "outputList"):
            translated_params = translated_meta[key][list_key]
            assert [p["key"] for p in translated_params] == [p["key"] for p in atomic[list_key]]
            assert [p["types"] for p in translated_params] == [p["types"] for p in atomic[list_key]]
            for translated, original in zip(translated_params, atomic[list_key]):
                assert [o["value"] for o in translated.get("options") or []] == [
                    o["value"] for o in original.get("options") or []
                ]


def test_meta_generation_is_deterministic(component_dir, tmp_path):
    """连续两次生成结果必须一致，否则每次构建都会产生无意义的 diff。"""
    import shutil
    import subprocess
    import sys

    outputs = []
    for index in range(2):
        work = tmp_path / f"run-{index}"
        work.mkdir()
        for name in ("pyproject.toml", "config.yaml", "meta.py"):
            shutil.copy(component_dir / name, work / name)
        shutil.copytree(component_dir / "locale", work / "locale")
        result = subprocess.run(
            [sys.executable, "meta.py"],
            cwd=work,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        outputs.append(
            {
                rel: _read_json(work / rel)
                for rel in (
                    "meta.json",
                    "resources/zh_CN/meta.json",
                    "resources/zh_CN/tree.json",
                    "resources/en_US/meta.json",
                    "resources/en_US/tree.json",
                )
            }
        )
    assert outputs[0] == outputs[1]
