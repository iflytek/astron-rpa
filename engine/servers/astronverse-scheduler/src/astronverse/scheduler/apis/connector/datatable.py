import json
import os
from typing import Optional

from astronverse.scheduler.apis.response import ResCode, res_msg
from astronverse.scheduler.core.datatable.excel_service import ExcelService
from astronverse.scheduler.core.datatable.file_watcher import AsyncFileWatcher
from astronverse.scheduler.core.svc import Svc, get_svc
from astronverse.scheduler.logger import logger
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


# ==================== 请求模型 ====================


class OpenDataTableRequest(BaseModel):
    """打开数据表格请求"""

    project_id: str  # 工程ID
    filename: str  # 文件名（不含扩展名）


class UpdateCellsRequest(BaseModel):
    """更新单元格请求"""

    project_id: str  # 工程ID
    filename: str  # 文件名
    updates: list[dict]  # 更新列表 [{"sheet": str, "row": int, "col": int, "value": any}]


class CloseDataTableRequest(BaseModel):
    """关闭数据表格请求"""

    project_id: str  # 工程ID
    filename: str  # 文件名


# ==================== 工具函数 ====================


def get_project_dir(svc: Svc, project_id: str) -> str:
    """
    获取工程目录路径（工程ID目录下的astron目录）

    Args:
        svc: 服务上下文
        project_id: 工程ID

    Returns:
        工程目录的完整路径（{venv_base_dir}/{project_id}/astron）
    """
    return os.path.join(svc.config.venv_base_dir, project_id, "astron")


def ensure_project_dir(svc: Svc, project_id: str) -> str:
    """
    确保工程目录存在，如果不存在则创建

    Args:
        svc: 服务上下文
        project_id: 工程ID

    Returns:
        工程目录的完整路径
    """
    project_dir = get_project_dir(svc, project_id)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir, exist_ok=True)
        logger.info(f"Created project directory: {project_dir}")
    return project_dir


def get_excel_service(svc: Svc, project_id: str) -> ExcelService:
    """
    获取 Excel 服务实例

    Args:
        svc: 服务上下文
        project_id: 工程ID

    Returns:
        ExcelService 实例
    """
    project_dir = get_project_dir(svc, project_id)
    return ExcelService(project_dir)


# ==================== 活跃的文件监听器管理 ====================

# 存储活跃的 AsyncFileWatcher 实例，key 为文件路径
_active_watchers: dict[str, AsyncFileWatcher] = {}


def get_active_watcher(file_path: str) -> Optional[AsyncFileWatcher]:
    """获取活跃的文件监听器"""
    return _active_watchers.get(os.path.normpath(file_path))


def set_active_watcher(file_path: str, watcher: AsyncFileWatcher):
    """设置活跃的文件监听器"""
    _active_watchers[os.path.normpath(file_path)] = watcher


def remove_active_watcher(file_path: str):
    """移除活跃的文件监听器"""
    normalized_path = os.path.normpath(file_path)
    if normalized_path in _active_watchers:
        del _active_watchers[normalized_path]


# ==================== SSE 接口 ====================


@router.get("/stream")
async def datatable_stream(project_id: str, filename: str, svc: Svc = Depends(get_svc)):
    """
    SSE 流式接口：打开/创建 Excel 文件，流式返回数据，并持续监听文件变更

    - 如果工程目录不存在，会自动创建
    - 如果文件不存在，会自动创建空白 Excel 文件
    - 首先流式返回 Excel 数据（逐行发送）
    - 然后持续监听文件变更，有变更时推送通知

    Query Args:
        project_id: 工程ID
        filename: Excel 文件名（不含扩展名）

    SSE Events:
        - created: 文件被创建（之前不存在）
        - sheet_start: 工作表开始，包含 sheet 名称和行列数
        - row: 行数据
        - sheet_end: 工作表结束
        - complete: 数据加载完成
        - file_changed: 文件被外部修改
        - file_deleted: 文件被删除
        - heartbeat: 心跳保持连接
        - error: 错误信息
    """

    async def event_generator():
        watcher = None

        try:
            # 1. 确保工程目录存在
            ensure_project_dir(svc, project_id)

            excel_service = get_excel_service(svc, project_id)
            file_path = excel_service.get_file_path(filename)

            # 2. 检查文件是否存在，不存在则抛出错误
            if not excel_service.file_exists(filename):
                raise FileNotFoundError(f"File not found: {filename}")

            # # 3. 流式读取 Excel 数据
            # for row_data in excel_service.read_file_stream(filename):
            #     event_type = row_data.get("type", "data")
            #     yield format_sse_event(event_type, row_data)

            # 4. 启动文件监听
            watcher = AsyncFileWatcher(file_path)
            set_active_watcher(file_path, watcher)

            # 5. 持续监听文件变更
            async for event in watcher.start():
                yield format_sse_event(event["type"], event)

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            yield format_sse_event("error", {"message": str(e)})
        except Exception as e:
            logger.exception(f"Error in datatable stream: {e}")
            yield format_sse_event("error", {"message": str(e)})
        finally:
            # 清理资源
            if watcher:
                watcher.stop()
                remove_active_watcher(file_path)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def format_sse_event(event_type: str, data: dict) -> str:
    """
    格式化 SSE 事件

    Args:
        event_type: 事件类型
        data: 事件数据

    Returns:
        SSE 格式的字符串
    """
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {json_data}\n\n"


# ==================== REST API 接口 ====================


@router.post("/open")
def datatable_open(req: OpenDataTableRequest, svc: Svc = Depends(get_svc)):
    """
    打开/创建 Excel 文件（一次性返回全部数据）

    - 如果工程目录不存在，会自动创建
    - 如果文件不存在，会自动创建空白 Excel 文件
    - 如果需要处理大文件，建议使用 /stream 接口

    Args:
        req: 包含 project_id 和 filename 的请求体

    Returns:
        Excel 文件的完整数据
    """
    try:
        # 1. 确保工程目录存在
        ensure_project_dir(svc, req.project_id)

        excel_service = get_excel_service(svc, req.project_id)

        # 2. 检查文件是否存在，不存在则创建
        created = False
        if not excel_service.file_exists(req.filename):
            excel_service.create_file(req.filename)
            created = True

        # 3. 读取文件数据
        data = excel_service.read_file(req.filename)
        data["project_id"] = req.project_id
        data["created"] = created

        return res_msg(code=ResCode.SUCCESS, msg="ok", data=data)

    except Exception as e:
        logger.exception(f"Error opening datatable: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e))


@router.post("/update-cells")
def datatable_update_cells(req: UpdateCellsRequest, svc: Svc = Depends(get_svc)):
    """
    更新指定单元格（增量更新）

    Args:
        req: 包含 project_id、filename 和 updates 列表的请求体

    Returns:
        操作结果
    """
    try:
        # 检查工程目录是否存在
        project_dir = get_project_dir(svc, req.project_id)
        logger.info(f"Updating cells in {project_dir}")
        if not os.path.exists(project_dir):
            return res_msg(code=ResCode.ERR, msg=f"Project directory not found: {project_dir}")

        excel_service = get_excel_service(svc, req.project_id)

        # 检查文件是否存在
        if not excel_service.file_exists(req.filename):
            return res_msg(code=ResCode.ERR, msg=f"File not found: {req.filename}")

        file_path = excel_service.get_file_path(req.filename)

        # 暂停文件监听，避免自触发
        watcher = get_active_watcher(file_path)
        if watcher:
            watcher.pause_watching(duration=2.0)

        # 更新单元格
        excel_service.update_cells(req.filename, req.updates)

        return res_msg(
            code=ResCode.SUCCESS,
            msg="ok",
            data={"project_id": req.project_id, "filename": req.filename, "updated": len(req.updates)},
        )

    except FileNotFoundError as e:
        return res_msg(code=ResCode.ERR, msg=f"File not found: {req.filename}")
    except Exception as e:
        logger.exception(f"Error updating cells: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e))


@router.post("/close")
def datatable_close(req: CloseDataTableRequest, svc: Svc = Depends(get_svc)):
    """
    关闭数据表格，停止文件监听

    Args:
        req: 包含 project_id 和 filename 的请求体

    Returns:
        操作结果
    """
    try:
        excel_service = get_excel_service(svc, req.project_id)
        file_path = excel_service.get_file_path(req.filename)

        # 停止文件监听
        watcher = get_active_watcher(file_path)
        if watcher:
            watcher.stop()
            remove_active_watcher(file_path)

        return res_msg(code=ResCode.SUCCESS, msg="ok", data={"project_id": req.project_id, "filename": req.filename})

    except Exception as e:
        logger.exception(f"Error closing datatable: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e))


@router.post("/delete")
def datatable_delete(req: CloseDataTableRequest, svc: Svc = Depends(get_svc)):
    """
    删除 Excel 文件

    Args:
        req: 包含 project_id 和 filename 的请求体

    Returns:
        操作结果
    """
    try:
        excel_service = get_excel_service(svc, req.project_id)
        file_path = excel_service.get_file_path(req.filename)

        # 先停止文件监听
        watcher = get_active_watcher(file_path)
        if watcher:
            watcher.stop()
            remove_active_watcher(file_path)

        # 删除文件
        deleted = excel_service.delete_file(req.filename)

        if deleted:
            return res_msg(
                code=ResCode.SUCCESS,
                msg="ok",
                data={"project_id": req.project_id, "filename": req.filename, "deleted": True},
            )
        else:
            return res_msg(code=ResCode.ERR, msg="File not found")

    except Exception as e:
        logger.exception(f"Error deleting datatable: {e}")
        return res_msg(code=ResCode.ERR, msg=str(e))
