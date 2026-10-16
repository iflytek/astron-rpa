import json
import os
from dataclasses import field
from typing import Annotated

from astronverse.scheduler.core.svc import Svc, get_svc
from astronverse.scheduler.logger import logger
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

router = APIRouter()


class MetaKeys(BaseModel):
    """定义获取 meta 数据的参数。"""

    keys: list[str] = field(default_factory=list)


def _resource_dir(svc: Svc) -> str | None:
    """Resolve the Engine resources directory from the scheduler config file."""
    if not svc.config or not svc.config.conf_file:
        return None
    return os.path.dirname(os.path.abspath(os.fspath(svc.config.conf_file)))


def _locale(request: Request) -> str:
    """Prefer the custom header because browser JavaScript cannot override Accept-Language."""
    lang = request.headers.get("x-language") or request.headers.get("accept-language", "zh_CN")
    return "en_US" if lang.strip().lower().startswith("en") else "zh_CN"


def _load_meta_file(svc: Svc, locale: str, filename: str):
    resource_dir = _resource_dir(svc)
    if not resource_dir:
        return None

    file_path = os.path.join(resource_dir, "meta", locale, filename)
    if not os.path.exists(file_path):
        return None

    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


@router.post("/list")
def get_meta_list(request: Request, params: MetaKeys, svc: Annotated[Svc, Depends(get_svc)]):
    """获取指定语言的原子能力 meta 数据，支持按 atomKey 筛选。"""
    try:
        meta_data = _load_meta_file(svc, _locale(request), "meta.json")
        if meta_data is None:
            return {"code": "500001", "message": "Meta data file not found", "data": None}

        if not params.keys:
            return {"code": "000000", "message": "", "data": meta_data}

        filtered_data = [item for item in meta_data if item.get("atomKey") in params.keys]
        return {"code": "000000", "message": "", "data": filtered_data}
    except Exception as exc:
        logger.exception(exc)
        return {"code": "500001", "message": str(exc), "data": None}


@router.post("/tree")
def get_meta_tree(request: Request, svc: Annotated[Svc, Depends(get_svc)]):
    """获取指定语言的原子能力树数据。"""
    try:
        tree_data = _load_meta_file(svc, _locale(request), "tree.json")
        if tree_data is None:
            return {"code": "500001", "message": "Tree data file not found", "data": None}

        return {
            "code": "000000",
            "message": "",
            "data": json.dumps(tree_data, ensure_ascii=False),
        }
    except Exception as exc:
        logger.exception(exc)
        return {"code": "500001", "message": str(exc), "data": None}
