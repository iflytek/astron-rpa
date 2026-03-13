from __future__ import annotations

import logging
import subprocess

from astronverse.openclaw.config import config
from astronverse.openclaw.launcher import (
    LauncherError,
    build_env,
    detect_existing_state,
    detect_installed_command,
    install_from_source,
    launch,
    resolve_command,
    sync_prepared_files,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("astronverse.openclaw")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_openclaw_process: subprocess.Popen | None = None


@app.get("/health")
async def health():
    return {"code": 200, "message": "ok"}


@app.get("/status")
async def status():
    """返回 OpenClaw 进程的当前状态。"""
    has_installed = detect_installed_command()
    has_state = detect_existing_state(config)

    process_alive = False
    pid = None
    if _openclaw_process is not None:
        pid = _openclaw_process.pid
        process_alive = _openclaw_process.poll() is None

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "installed_command": has_installed,
            "existing_state": has_state,
            "openclaw_home": str(config.openclaw_home),
            "workspace": str(config.default_workspace),
            "process_alive": process_alive,
            "pid": pid,
        },
    }


@app.get("/check-install")
async def check_install():
    """检测 OpenClaw 是否已安装：先查命令是否可用，再查 .openclaw 目录是否存在。"""
    command_ok = detect_installed_command()
    state_ok = detect_existing_state(config)
    installed = command_ok or state_ok

    detail = {
        "installed": installed,
        "command_available": command_ok,
        "home_exists": state_ok,
        "openclaw_home": str(config.openclaw_home),
    }

    if not installed:
        return {"code": 200, "message": "未安装", "data": detail}

    reason = "命令可用" if command_ok else ".openclaw 目录已存在"
    return {"code": 200, "message": f"已安装（{reason}）", "data": detail}


@app.post("/launch")
async def launch_openclaw(args: list[str] | None = None):
    """启动 OpenClaw 进程。"""
    global _openclaw_process

    if _openclaw_process is not None and _openclaw_process.poll() is None:
        return {
            "code": 409,
            "message": "OpenClaw 已在运行中",
            "data": {"pid": _openclaw_process.pid},
        }

    try:
        _openclaw_process = launch(config, forward_args=args)
        return {
            "code": 200,
            "message": "OpenClaw 启动成功",
            "data": {"pid": _openclaw_process.pid if _openclaw_process else None},
        }
    except LauncherError as exc:
        logger.error("启动 OpenClaw 失败: %s", exc)
        return {"code": 500, "message": f"启动失败: {exc}"}


@app.post("/stop")
async def stop_openclaw():
    """停止 OpenClaw 进程。"""
    global _openclaw_process

    if _openclaw_process is None or _openclaw_process.poll() is not None:
        _openclaw_process = None
        return {"code": 200, "message": "OpenClaw 未在运行"}

    pid = _openclaw_process.pid
    _openclaw_process.terminate()
    try:
        _openclaw_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _openclaw_process.kill()
        _openclaw_process.wait(timeout=5)
    _openclaw_process = None

    logger.info("OpenClaw 进程已停止, pid=%s", pid)
    return {"code": 200, "message": "OpenClaw 已停止", "data": {"pid": pid}}


@app.post("/sync")
async def sync_files():
    """同步预配置文件到 OpenClaw home 目录。"""
    try:
        changes = sync_prepared_files(config)
        return {"code": 200, "message": "同步完成", "data": {"changes": changes}}
    except Exception as exc:
        logger.error("同步失败: %s", exc)
        return {"code": 500, "message": f"同步失败: {exc}"}


@app.post("/install")
async def install():
    """从源码安装 OpenClaw 依赖。"""
    try:
        env = build_env(config)
        changes = install_from_source(config, env)
        return {"code": 200, "message": "安装完成", "data": {"changes": changes}}
    except LauncherError as exc:
        logger.error("安装失败: %s", exc)
        return {"code": 500, "message": f"安装失败: {exc}"}


@app.get("/resolve")
async def resolve(args: str = "gateway"):
    """解析将要执行的命令（不实际执行）。"""
    try:
        forward_args = args.split(",") if args else list(config.default_args)
        command, mode = resolve_command(config, forward_args)
        return {
            "code": 200,
            "message": "ok",
            "data": {"command": command, "mode": mode},
        }
    except LauncherError as exc:
        return {"code": 500, "message": str(exc)}


@app.on_event("shutdown")
async def on_shutdown():
    """服务关闭时，清理 OpenClaw 子进程。"""
    global _openclaw_process
    if _openclaw_process is not None and _openclaw_process.poll() is None:
        logger.info("服务关闭，停止 OpenClaw 进程 pid=%s", _openclaw_process.pid)
        _openclaw_process.terminate()
        try:
            _openclaw_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _openclaw_process.kill()
        _openclaw_process = None
