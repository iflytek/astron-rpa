import time
import winreg
from typing import Optional

import win32com
import win32com.client
from astronverse.actionlib.logger import logger
from astronverse.excel import ApplicationType
from astronverse.excel.excel_obj import ExcelObj


def get_default_excel_application():
    """
    获取系统默认的Excel应用类型

    通过检查Windows注册表来确定默认的Excel应用程序是Microsoft Excel还是WPS。

    Returns:
        ApplicationType: 默认的Excel应用类型，如果无法确定则返回ApplicationType.EXCEL
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Excel.Sheet.12\shell\open\command")
        default_value, _ = winreg.QueryValueEx(key, None)
        winreg.CloseKey(key)

        if "et.exe" in default_value.lower():
            return ApplicationType.WPS
        elif "excel.exe" in default_value.lower():
            return ApplicationType.EXCEL
    except FileNotFoundError:
        return ApplicationType.EXCEL


def _create_app(params: str, retry: int = 0, retry_delay: float = 0.5):
    """
    创建Excel应用对象，可选重试机制
    """
    max_attempts = retry + 1  # 总尝试次数 = 重试次数 + 1次初始尝试

    for attempt in range(max_attempts):
        try:
            # 优先使用cache，性能更好
            return win32com.client.gencache.EnsureDispatch(params)
        except Exception as e:
            # 降级方案：使用Dispatch
            try:
                return win32com.client.Dispatch(params)
            except Exception as e:
                if attempt < max_attempts - 1:
                    logger.warning(
                        f"创建Excel应用失败 (尝试 {attempt + 1}/{max_attempts}): {params}, "
                        f"错误: {e}, {retry_delay:.2f}秒后重试..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(f"创建Excel应用失败: {params}, 错误: {e}, 已达到最大重试次数")
    return None


def _get_app(params: str, retry: int = 0, retry_delay: float = 0.5):
    """
    获取已存在的Excel应用对象，可选重试机制
    """
    max_attempts = retry + 1  # 总尝试次数 = 重试次数 + 1次初始尝试

    for attempt in range(max_attempts):
        try:
            return win32com.client.GetObject(Class=params)
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(
                    f"获取Excel应用失败 (尝试 {attempt + 1}/{max_attempts}): {params}, "
                    f"错误: {e}, {retry_delay:.2f}秒后重试..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(f"获取Excel应用失败: {params}, 错误: {e}, 已达到最大重试次数")
    return None


def _get_key(default_application: ApplicationType = ApplicationType.DEFAULT):
    """获取Excel应用的注册表键值"""

    if default_application == ApplicationType.DEFAULT:
        default_application = get_default_excel_application()
        if default_application == ApplicationType.WPS:
            keys = ["Ket.Application", "et.Application", "Excel.Application"]
        elif default_application == ApplicationType.EXCEL:
            keys = ["Excel.Application", "Ket.Application", "et.Application"]
        else:
            keys = ["Ket.Application", "et.Application", "Excel.Application"]
    elif default_application == ApplicationType.WPS:
        keys = ["Ket.Application", "et.Application"]
    elif default_application == ApplicationType.EXCEL:
        keys = ["Excel.Application"]
    else:
        keys = ["Ket.Application", "et.Application", "Excel.Application"]
    return keys


class Application:
    @staticmethod
    def init_app(
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = None,
        retry: int = 0,
        retry_delay: float = 0.5,
        prefer_existing: bool = True,
    ) -> object:
        """初始化 Excel 应用"""

        application = None
        keys = _get_key(default_application=default_application)

        if prefer_existing:
            # 如果 prefer_existing=True，先尝试获取已存在的实例
            for key in keys:
                application = _get_app(key, retry=retry, retry_delay=retry_delay)
                if application:
                    break
        if not application:
            # 如果 prefer_existing=False 或 GetObject 失败，则创建新实例
            for key in keys:
                application = _create_app(key, retry=retry, retry_delay=retry_delay)
                if application:
                    break

        if not application:
            try:
                win32com.client.gencache.Rebuild()
                win32com.client.gencache.EnsureModule("{00020813-0000-0000-C000-000000000046}", 0, 8, 7)
            except Exception:
                raise Exception("兜底失败，请尝试手动删除 %LOCALAPPDATA%\\Temp\\gen_py 目录再运行！")

            # 重建缓存后，再次尝试（优先获取已存在的实例）
            if prefer_existing:
                # 如果 prefer_existing=True，先尝试获取已存在的实例
                for key in keys:
                    application = _get_app(key, retry=retry, retry_delay=retry_delay)
                    if application:
                        break
            if not application:
                # 如果 prefer_existing=False 或 GetObject 失败，则创建新实例
                for key in keys:
                    application = _create_app(key, retry=retry, retry_delay=retry_delay)
                    if application:
                        break

        # 异常报错
        if not application:
            raise Exception("未检测到Excel或WPS应用")

        if visible_flag is not None:
            application.Visible = visible_flag
        # 始终禁用显示警告，避免弹窗中断自动化流程
        # 这样可以自动处理文件覆盖、删除工作表等操作，提高脚本稳定性
        application.DisplayAlerts = False
        return application

    @staticmethod
    def quit_app(default_application: ApplicationType = ApplicationType.DEFAULT, save_changes: bool = False):
        """退出 Excel 应用"""

        keys = _get_key(default_application=default_application)

        for key in keys:
            application = _get_app(key, retry=0, retry_delay=0)
            if not application:
                continue
            try:
                workbooks_count = application.Workbooks.Count
                for i in range(workbooks_count, 0, -1):
                    workbook = application.Workbooks(i)
                    workbook.Close(SaveChanges=save_changes)
                application.Quit()
            except Exception as e:
                logger.warning("关闭异常 {}".format(e))
                pass

    @staticmethod
    def create_workbook(application, file_path: str = "", password: str = "") -> ExcelObj:
        """创建新工作簿"""
        workbook = application.Workbooks.Add()
        if file_path:
            workbook.SaveAs(Filename=file_path, ReadOnlyRecommended=False, ConflictResolution=2, Password=password)
        return ExcelObj(obj=workbook, path=file_path or "")

    @staticmethod
    def open_workbook(application, file_path: str, password: str = "", update_links: bool = True) -> ExcelObj:
        """打开工作簿"""

        workbook = application.Workbooks.Open(
            Filename=file_path, UpdateLinks=update_links, Password=password, ReadOnly=False, Format=None
        )
        return ExcelObj(obj=workbook, path=file_path or "")

    @staticmethod
    def get_existing_workbook(application, match_name: str) -> Optional[ExcelObj]:
        """获取已打开的工作簿"""
        workbooks_count = application.Workbooks.Count
        for i in range(workbooks_count, 0, -1):
            workbook = application.Workbooks(i)
            if match_name in workbook.Name:
                return ExcelObj(obj=workbook)
        return None

    @staticmethod
    def save_workbook(excel_obj: ExcelObj, file_path: str = "", password: str = ""):
        workbook = excel_obj.obj
        if file_path:
            workbook.SaveAs(Filename=file_path, ReadOnlyRecommended=False, ConflictResolution=2, Password=password)
        else:
            workbook.Save()

    @staticmethod
    def close_workbook(excel_obj: ExcelObj, save_changes: bool = True):
        workbook = excel_obj.obj
        workbook.Close(SaveChanges=save_changes)
