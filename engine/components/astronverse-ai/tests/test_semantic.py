"""Offline contract tests; only the engine runtime and HTTP transport are mocked."""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

COMPONENT = Path(__file__).resolve().parents[1]
OPTIONS = [{"id": "refund", "label": "退款"}, {"id": "delivery", "label": "物流"}]


@pytest.fixture
def semantic(monkeypatch):
    atomic = ModuleType("astronverse.actionlib.atomic")
    atomic.atomicMg = SimpleNamespace(
        atomic=lambda *args, **kwargs: lambda func: func,
        param=lambda *args, **kwargs: None,
        cfg=lambda: {"GATEWAY_PORT": 13579},
    )
    monkeypatch.setitem(sys.modules, "astronverse.actionlib.atomic", atomic)
    spec = importlib.util.spec_from_file_location("semantic_under_test", COMPONENT / "src/astronverse/ai/semantic.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_component_metadata_exposes_semantic_choice():
    metadata = json.loads((COMPONENT / "meta.json").read_text())
    assert "SemanticAI.choose" in metadata, "semantic choice must be available in designer metadata"
    node = metadata["SemanticAI.choose"]
    assert [item["key"] for item in node["inputList"]] == ["instruction", "text", "options"]
    assert node["outputList"][0]["types"] == "Dict"


@pytest.mark.parametrize(
    "result",
    [
        {"status": "matched", "selected_id": "refund", "confidence": 0.9},
        {"status": "abstain", "selected_id": None, "confidence": 0.8},
    ],
)
def test_returns_valid_decisions(semantic, monkeypatch, result):
    response = Mock()
    response.json.return_value = result
    post = Mock(return_value=response)
    monkeypatch.setattr(semantic.requests, "post", post)
    assert semantic.SemanticAI.choose("分类", "我要退款", OPTIONS) == result
    post.assert_called_once_with(
        "http://127.0.0.1:13579/api/rpa-ai-service/v1/decision/choice",
        json={"instruction": "分类", "text": "我要退款", "options": OPTIONS},
        timeout=(5, 35),
    )
    response.raise_for_status.assert_called_once()
    response.close.assert_called_once()


@pytest.mark.parametrize(
    "options",
    [
        [],
        [{"id": "x", "label": " "}],
        [{"id": " ", "label": "x"}],
        [{"id": "__abstain__", "label": "x"}],
        OPTIONS * 2,
        [{"id": str(i), "label": "x"} for i in range(255)],
        [{"id": "x"}],
        "not a list",
    ],
)
def test_rejects_invalid_options_before_http(semantic, monkeypatch, options):
    post = Mock()
    monkeypatch.setattr(semantic.requests, "post", post)
    with pytest.raises(ValueError):
        semantic.SemanticAI.choose("分类", "文本", options)
    post.assert_not_called()


@pytest.mark.parametrize(
    "result",
    [
        None,
        [],
        {},
        {"data": {"status": "abstain"}},
        {"status": "matched", "selected_id": "unknown", "confidence": 0.8},
        {"status": "matched", "selected_id": None, "confidence": 0.8},
        {"status": "abstain", "selected_id": "refund", "confidence": 0.8},
        {"status": "abstain", "confidence": 0.8},
        {"status": "error", "selected_id": None, "confidence": 0.8},
        *[
            {"status": "matched", "selected_id": "refund", "confidence": value}
            for value in (True, "0.9", -1, 2, float("nan"), float("inf"))
        ],
    ],
)
def test_invalid_response_is_not_abstention(semantic, monkeypatch, result):
    response = Mock()
    response.json.return_value = result
    monkeypatch.setattr(semantic.requests, "post", Mock(return_value=response))
    with pytest.raises(ValueError, match="Invalid semantic choice response"):
        semantic.SemanticAI.choose("分类", "文本", OPTIONS)
    response.close.assert_called_once()


@pytest.mark.parametrize("failure_name", ["Timeout", "HTTPError"])
def test_http_failures_propagate(semantic, monkeypatch, failure_name):
    failure = getattr(semantic.requests, failure_name)
    response = Mock()
    response.raise_for_status.side_effect = failure("upstream failed")
    monkeypatch.setattr(semantic.requests, "post", Mock(return_value=response))
    with pytest.raises(failure):
        semantic.SemanticAI.choose("分类", "文本", OPTIONS)
    response.close.assert_called_once()


def test_connection_timeout_propagates(semantic, monkeypatch):
    monkeypatch.setattr(semantic.requests, "post", Mock(side_effect=semantic.requests.Timeout))
    with pytest.raises(semantic.requests.Timeout):
        semantic.SemanticAI.choose("分类", "文本", OPTIONS)


@pytest.mark.parametrize(("instruction", "text"), [(" ", "text"), ("classify", ""), (None, "text"), ("classify", 3)])
def test_rejects_empty_or_nontext_input(semantic, monkeypatch, instruction, text):
    post = Mock()
    monkeypatch.setattr(semantic.requests, "post", post)
    with pytest.raises(ValueError):
        semantic.SemanticAI.choose(instruction, text, OPTIONS)
    post.assert_not_called()


def test_normalizes_ids_like_backend(semantic, monkeypatch):
    response = Mock()
    response.json.return_value = {"status": "matched", "selected_id": "refund", "confidence": 0.9}
    post = Mock(return_value=response)
    monkeypatch.setattr(semantic.requests, "post", post)
    result = semantic.SemanticAI.choose(" classify ", " text ", [{"id": " refund ", "label": " 退款 "}])
    assert result["selected_id"] == "refund"
    assert post.call_args.kwargs["json"] == {
        "instruction": "classify",
        "text": "text",
        "options": [{"id": "refund", "label": "退款"}],
    }


def test_rejects_duplicate_normalized_ids(semantic, monkeypatch):
    post = Mock()
    monkeypatch.setattr(semantic.requests, "post", post)
    with pytest.raises(ValueError):
        semantic.SemanticAI.choose("分类", "文本", [{"id": "x", "label": "A"}, {"id": " x ", "label": "B"}])
    post.assert_not_called()


def test_invalid_json_closes_response(semantic, monkeypatch):
    response = Mock()
    response.json.side_effect = ValueError("invalid JSON")
    monkeypatch.setattr(semantic.requests, "post", Mock(return_value=response))
    with pytest.raises(ValueError):
        semantic.SemanticAI.choose("分类", "文本", OPTIONS)
    response.close.assert_called_once()


def test_initialization_and_upgrade_publish_the_same_node():
    repo = COMPONENT.parents[2]
    migration = (repo / "docker/migrations/20260923_add_semantic_choice.sql").read_text()
    initialization = (repo / "docker/volumes/mysql/init_c_atom_meta_new_data.sql").read_text()
    assert initialization.endswith(migration)
    sql_json = migration.split("SELECT 'SemanticAI.choose', '", 1)[1].split("'\nWHERE NOT EXISTS", 1)[0]
    published = json.loads(sql_json.replace("''", "'").replace("\\\\", "\\"))
    assert published == json.loads((COMPONENT / "meta.json").read_text())["SemanticAI.choose"]
