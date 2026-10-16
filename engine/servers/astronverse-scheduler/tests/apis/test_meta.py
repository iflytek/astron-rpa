import json
from types import SimpleNamespace

from astronverse.scheduler.apis import meta
from astronverse.scheduler.core.svc import get_svc
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def _write_meta_files(resource_dir, locale, meta_data, tree_data):
    locale_dir = resource_dir / "meta" / locale
    locale_dir.mkdir(parents=True)
    (locale_dir / "meta.json").write_text(json.dumps(meta_data), encoding="utf-8")
    (locale_dir / "tree.json").write_text(json.dumps(tree_data), encoding="utf-8")


def _client(resource_dir):
    svc = SimpleNamespace(config=SimpleNamespace(conf_file=resource_dir / "conf.yaml"))
    app = FastAPI()
    app.dependency_overrides[get_svc] = lambda: svc
    app.include_router(meta.router, prefix="/meta", dependencies=[Depends(get_svc)])
    return TestClient(app)


def test_meta_routes_select_locale_filter_meta_and_serialize_tree(tmp_path):
    zh_meta = [{"atomKey": "zh.atom", "atomContent": "中文"}]
    en_meta = [
        {"atomKey": "en.atom", "atomContent": "English"},
        {"atomKey": "other.atom", "atomContent": "Other"},
    ]
    tree = {"atomicTree": [{"key": "en.atom"}]}
    _write_meta_files(tmp_path, "zh_CN", zh_meta, {"locale": "zh"})
    _write_meta_files(tmp_path, "en_US", en_meta, tree)

    with _client(tmp_path) as client:
        response = client.post("/meta/list", json={"keys": ["en.atom"]}, headers={"X-Language": "en-US"})
        assert response.json() == {"code": "000000", "message": "", "data": [en_meta[0]]}

        response = client.post("/meta/tree", headers={"Accept-Language": "en-US"})
        assert response.json() == {
            "code": "000000",
            "message": "",
            "data": json.dumps(tree, ensure_ascii=False),
        }


def test_meta_routes_report_missing_files(tmp_path):
    with _client(tmp_path) as client:
        response = client.post("/meta/list", json={})

    assert response.json() == {
        "code": "500001",
        "message": "Meta data file not found",
        "data": None,
    }
