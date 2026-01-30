"""
凭证管理 API 路由
"""

from astronverse.scheduler.apis.response import ResCode, res_msg
from astronverse.scheduler.core.credential import CredentialService
from astronverse.scheduler.logger import logger
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class CreateCredentialRequest(BaseModel):
    """创建凭证请求"""

    name: str
    password: str


class DeleteCredentialRequest(BaseModel):
    """删除凭证请求"""

    name: str


@router.get("/list")
def credential_list():
    """
    获取凭证列表
    """
    try:
        credentials = CredentialService.list_credentials()
        return res_msg(code=ResCode.SUCCESS, msg="success", data=credentials)
    except Exception as e:
        logger.exception(f"获取凭证列表失败: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/create")
def credential_create(req: CreateCredentialRequest):
    """
    创建凭证
    """
    try:
        success = CredentialService.create_credential(req.name, req.password)
        if success:
            return res_msg(code=ResCode.SUCCESS, msg="success", data=None)
        else:
            return res_msg(code=ResCode.ERR, msg="创建凭证失败", data=None)
    except Exception as e:
        logger.exception(f"创建凭证失败: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/delete")
def credential_delete(req: DeleteCredentialRequest):
    """
    删除凭证
    """
    try:
        success = CredentialService.delete_credential(req.name)
        if success:
            return res_msg(code=ResCode.SUCCESS, msg="success", data=None)
        else:
            return res_msg(code=ResCode.ERR, msg="删除凭证失败", data=None)
    except Exception as e:
        logger.exception(f"删除凭证失败: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.get("/exists")
def credential_exists(name: str = Query(..., description="凭证名称")):
    """
    检查凭证是否存在
    """
    try:
        exists = CredentialService.exists(name)
        return res_msg(code=ResCode.SUCCESS, msg="success", data={"exists": exists})
    except Exception as e:
        logger.exception(f"检查凭证是否存在失败: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)
