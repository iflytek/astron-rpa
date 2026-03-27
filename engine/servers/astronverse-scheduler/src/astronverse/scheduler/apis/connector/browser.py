import os
from dataclasses import field
from enum import Enum

from astronverse.scheduler.apis.response import ResCode, res_msg
from astronverse.scheduler.core.svc import Svc, get_svc
from astronverse.scheduler.logger import logger
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

router = APIRouter()


class BrowserPlugin(BaseModel):
    """定义安装插件参数"""

    browser: str = "chrome"
    op: str = "install"


class BrowserType(Enum):
    CHROME = "CHROME"


class CheckBrowserPlugin(BaseModel):
    """定义检测安装插件参数"""

    browsers: list[str] = field(default_factory=list)

    @classmethod
    @field_validator("browsers", mode="before")
    def set_default_browsers(cls, v):
        default_browser_list = [browser.value.lower() for browser in BrowserType]
        if not v:
            return default_browser_list
        assert all(item in default_browser_list for item in v), "Invalid browser type in plugins"
        return v


@router.get("/plugins/get_support")
def browser_get_support():
    """
    获取插件支持的浏览器列表
    """
    try:
        from astronverse.browser_plugin.browser import ExtensionManager

        browsers = [b.value.lower() for b in ExtensionManager.get_support()]
        return res_msg(msg="获取成功", data={"browsers": browsers})
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="获取失败", data=None)


@router.post("/plugins/install")
def browser_install(plugin_op: BrowserPlugin, svc: Svc = Depends(get_svc)):
    """
    安装插件
    """
    try:
        from astronverse.browser_plugin import BrowserType as BPBrowserType
        from astronverse.browser_plugin.browser import ExtensionManager

        browser = BPBrowserType.init(plugin_op.browser)
        resource_dir = os.path.dirname(svc.config.conf_file)
        ex_manager = ExtensionManager(resource_dir, browser_type=browser)
        ex_manager.install()
        return res_msg(msg="安装成功", data=None)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="安装失败", data=None)


@router.post("/plugins/check_status")
def browser_check(options: CheckBrowserPlugin, svc: Svc = Depends(get_svc)):
    """
    检测插件状态
    """
    try:
        from astronverse.browser_plugin import BrowserType as BPBrowserType
        from astronverse.browser_plugin.browser import ExtensionManager

        resource_dir = os.path.dirname(svc.config.conf_file)
        check_result = dict()
        for browser in options.browsers:
            ex_manager = ExtensionManager(resource_dir, browser_type=BPBrowserType.init(browser))
            check_result[browser.lower()] = ex_manager.check_status()
        return res_msg(msg="", data=check_result)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="检测失败", data=None)


@router.post("/plugins/check_running")
def browser_check_running(plugin_op: BrowserPlugin, svc: Svc = Depends(get_svc)):
    """
    检测浏览器是否运行
    """
    try:
        from astronverse.browser_plugin import BrowserType as BPBrowserType
        from astronverse.browser_plugin.browser import ExtensionManager

        browser = BPBrowserType.init(plugin_op.browser)
        resource_dir = os.path.dirname(svc.config.conf_file)
        ex_manager = ExtensionManager(resource_dir, browser_type=browser)
        running = ex_manager.check_browser_running()
        return res_msg(msg="", data={"running": running})
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="检测失败", data=None)


@router.post("/plugins/install_all_updates")
def update_installed_plugins(svc: Svc = Depends(get_svc)):
    """
    更新已安装的浏览器插件
    """
    try:
        from astronverse.browser_plugin.browser import UpdateManager

        resource_dir = os.path.dirname(svc.config.conf_file)
        install_results = UpdateManager(resource_dir).update_installed_plugins()
        return res_msg(msg="更新完成", data=install_results)
    except Exception as e:
        logger.exception(e)
        return res_msg(code=ResCode.ERR, msg="更新失败", data=None)
