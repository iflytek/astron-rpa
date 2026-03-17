from __future__ import annotations

import json
import subprocess
from typing import Any, Literal

from astronverse.openclaw.config import config
from astronverse.openclaw.launcher import (
    LauncherError,
    build_env,
    detect_existing_state,
    detect_installed_command,
    install_from_source,
    launch,
    resolve_command,
    run_cli,
    sync_prepared_files,
)
from astronverse.openclaw.logger import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_openclaw_process: subprocess.Popen | None = None
_openclaw_forward_args: list[str] | None = None

ONBOARD_DOCS_URL = "https://docs.openclaw.ai/cli/onboard"
ONBOARD_PROVIDER_OPTIONS = (
    {
        "id": "anthropic-api-key",
        "auth_choice": "apiKey",
        "api_key_flag": "--anthropic-api-key",
        "label": "Anthropic",
        "api_key_label": "Anthropic API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "openai-api-key",
        "auth_choice": "openai-api-key",
        "api_key_flag": "--openai-api-key",
        "label": "OpenAI",
        "api_key_label": "OpenAI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "gemini-api-key",
        "auth_choice": "gemini-api-key",
        "api_key_flag": "--gemini-api-key",
        "label": "Google Gemini",
        "api_key_label": "Gemini API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "openrouter-api-key",
        "auth_choice": "openrouter-api-key",
        "api_key_flag": "--openrouter-api-key",
        "label": "OpenRouter",
        "api_key_label": "OpenRouter API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "mistral-api-key",
        "auth_choice": "mistral-api-key",
        "api_key_flag": "--mistral-api-key",
        "label": "Mistral",
        "api_key_label": "Mistral API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "moonshot-api-key",
        "auth_choice": "moonshot-api-key",
        "api_key_flag": "--moonshot-api-key",
        "label": "Kimi API (.ai)",
        "api_key_label": "Moonshot API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "moonshot-api-key-cn",
        "auth_choice": "moonshot-api-key-cn",
        "api_key_flag": "--moonshot-api-key",
        "label": "Kimi API (.cn)",
        "api_key_label": "Moonshot API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "kimi-code-api-key",
        "auth_choice": "kimi-code-api-key",
        "api_key_flag": "--kimi-code-api-key",
        "label": "Kimi Coding",
        "api_key_label": "Kimi Coding API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "modelstudio-api-key",
        "auth_choice": "modelstudio-api-key",
        "api_key_flag": "--modelstudio-api-key",
        "label": "Alibaba Cloud Model Studio (Global/Intl)",
        "api_key_label": "Model Studio API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "modelstudio-api-key-cn",
        "auth_choice": "modelstudio-api-key-cn",
        "api_key_flag": "--modelstudio-api-key-cn",
        "label": "Alibaba Cloud Model Studio (China)",
        "api_key_label": "Model Studio API Key (CN)",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "zai-api-key",
        "auth_choice": "zai-api-key",
        "api_key_flag": "--zai-api-key",
        "label": "Z.AI",
        "api_key_label": "Z.AI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "zai-global",
        "auth_choice": "zai-global",
        "api_key_flag": "--zai-api-key",
        "label": "Z.AI Global",
        "api_key_label": "Z.AI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "zai-cn",
        "auth_choice": "zai-cn",
        "api_key_flag": "--zai-api-key",
        "label": "Z.AI China",
        "api_key_label": "Z.AI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "zai-coding-global",
        "auth_choice": "zai-coding-global",
        "api_key_flag": "--zai-api-key",
        "label": "Z.AI Coding (Global)",
        "api_key_label": "Z.AI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "zai-coding-cn",
        "auth_choice": "zai-coding-cn",
        "api_key_flag": "--zai-api-key",
        "label": "Z.AI Coding (China)",
        "api_key_label": "Z.AI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "xiaomi-api-key",
        "auth_choice": "xiaomi-api-key",
        "api_key_flag": "--xiaomi-api-key",
        "label": "Xiaomi",
        "api_key_label": "Xiaomi API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "minimax-global-api",
        "auth_choice": "minimax-global-api",
        "api_key_flag": "--minimax-api-key",
        "label": "MiniMax Global",
        "api_key_label": "MiniMax API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "minimax-cn-api",
        "auth_choice": "minimax-cn-api",
        "api_key_flag": "--minimax-api-key",
        "label": "MiniMax China",
        "api_key_label": "MiniMax API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "kilocode-api-key",
        "auth_choice": "kilocode-api-key",
        "api_key_flag": "--kilocode-api-key",
        "label": "Kilo Gateway",
        "api_key_label": "Kilo Gateway API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "litellm-api-key",
        "auth_choice": "litellm-api-key",
        "api_key_flag": "--litellm-api-key",
        "label": "LiteLLM",
        "api_key_label": "LiteLLM API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "ai-gateway-api-key",
        "auth_choice": "ai-gateway-api-key",
        "api_key_flag": "--ai-gateway-api-key",
        "label": "Vercel AI Gateway",
        "api_key_label": "AI Gateway API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "synthetic-api-key",
        "auth_choice": "synthetic-api-key",
        "api_key_flag": "--synthetic-api-key",
        "label": "Synthetic",
        "api_key_label": "Synthetic API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "venice-api-key",
        "auth_choice": "venice-api-key",
        "api_key_flag": "--venice-api-key",
        "label": "Venice",
        "api_key_label": "Venice API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "together-api-key",
        "auth_choice": "together-api-key",
        "api_key_flag": "--together-api-key",
        "label": "Together AI",
        "api_key_label": "Together API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "huggingface-api-key",
        "auth_choice": "huggingface-api-key",
        "api_key_flag": "--huggingface-api-key",
        "label": "Hugging Face",
        "api_key_label": "Hugging Face Token",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "opencode-zen",
        "auth_choice": "opencode-zen",
        "api_key_flag": "--opencode-zen-api-key",
        "label": "OpenCode Zen catalog",
        "api_key_label": "OpenCode API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "opencode-go",
        "auth_choice": "opencode-go",
        "api_key_flag": "--opencode-go-api-key",
        "label": "OpenCode Go catalog",
        "api_key_label": "OpenCode API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "xai-api-key",
        "auth_choice": "xai-api-key",
        "api_key_flag": "--xai-api-key",
        "label": "xAI",
        "api_key_label": "xAI API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "qianfan-api-key",
        "auth_choice": "qianfan-api-key",
        "api_key_flag": "--qianfan-api-key",
        "label": "Qianfan",
        "api_key_label": "Qianfan API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "volcengine-api-key",
        "auth_choice": "volcengine-api-key",
        "api_key_flag": "--volcengine-api-key",
        "label": "Volcano Engine",
        "api_key_label": "Volcano Engine API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "byteplus-api-key",
        "auth_choice": "byteplus-api-key",
        "api_key_flag": "--byteplus-api-key",
        "label": "BytePlus",
        "api_key_label": "BytePlus API Key",
        "requires_api_key": True,
        "supports_custom_model": False,
    },
    {
        "id": "custom-api-key",
        "auth_choice": "custom-api-key",
        "api_key_flag": "--custom-api-key",
        "label": "Custom Provider",
        "api_key_label": "Custom Provider API Key",
        "requires_api_key": False,
        "supports_custom_model": True,
    },
    {
        "id": "ollama",
        "auth_choice": "ollama",
        "api_key_flag": None,
        "label": "Ollama",
        "api_key_label": None,
        "requires_api_key": False,
        "supports_custom_model": True,
    },
)
ONBOARD_PROVIDER_MAP = {item["id"]: item for item in ONBOARD_PROVIDER_OPTIONS}
SENSITIVE_FLAGS = {
    "--ai-gateway-api-key",
    "--anthropic-api-key",
    "--byteplus-api-key",
    "--custom-api-key",
    "--gemini-api-key",
    "--gateway-password",
    "--gateway-token",
    "--huggingface-api-key",
    "--kimi-code-api-key",
    "--kilocode-api-key",
    "--litellm-api-key",
    "--mistral-api-key",
    "--modelstudio-api-key",
    "--modelstudio-api-key-cn",
    "--moonshot-api-key",
    "--openai-api-key",
    "--opencode-go-api-key",
    "--opencode-zen-api-key",
    "--openrouter-api-key",
    "--qianfan-api-key",
    "--synthetic-api-key",
    "--token",
    "--together-api-key",
    "--venice-api-key",
    "--volcengine-api-key",
    "--xai-api-key",
    "--xiaomi-api-key",
    "--zai-api-key",
}


class OnboardRequest(BaseModel):
    auth_choice: str = Field(description="OpenClaw onboard 的 auth-choice 值")
    api_key: str | None = Field(default=None, description="供应商 API Key")
    custom_base_url: str | None = Field(default=None, description="自定义兼容服务地址")
    custom_model_id: str | None = Field(default=None, description="自定义模型 ID")
    custom_provider_id: str | None = Field(default=None, description="自定义 provider ID")
    custom_compatibility: Literal["openai", "anthropic"] = "openai"
    flow: Literal["quickstart", "advanced", "manual"] = "quickstart"
    secret_input_mode: Literal["plaintext", "ref"] = "plaintext"
    gateway_bind: Literal["loopback", "tailnet", "lan", "auto", "custom"] | None = None
    gateway_port: int | None = None
    workspace: str | None = None
    install_daemon: bool = False
    skip_channels: bool = True
    skip_health: bool = True
    skip_search: bool = True
    skip_skills: bool = True
    skip_ui: bool = True
    restart_if_running: bool = True


def _load_json_file(path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("读取 JSON 失败: %s, error=%s", path, exc)
        return None


def _configured_gateway_settings() -> tuple[int, str]:
    raw = _load_json_file(config.config_path) or _load_json_file(config.seed_root / "openclaw.runtime.json") or {}
    gateway = raw.get("gateway", {}) if isinstance(raw, dict) else {}
    port = gateway.get("port", 19878)
    bind = gateway.get("bind", "loopback")
    try:
        port = int(port)
    except (TypeError, ValueError):
        port = 19878
    if bind not in {"loopback", "tailnet", "lan", "auto", "custom"}:
        bind = "loopback"
    return port, bind


def _read_config_summary() -> dict[str, Any]:
    raw = _load_json_file(config.config_path)
    if raw is None:
        return {
            "config_exists": False,
            "primary_model": None,
            "workspace": str(config.default_workspace),
            "providers": [],
        }

    agents_defaults = raw.get("agents", {}).get("defaults", {})
    providers = raw.get("models", {}).get("providers", {})
    primary_model = agents_defaults.get("model", {}).get("primary")
    workspace = agents_defaults.get("workspace", str(config.default_workspace))
    provider_ids = sorted(providers.keys()) if isinstance(providers, dict) else []

    return {
        "config_exists": True,
        "primary_model": primary_model,
        "workspace": workspace,
        "providers": provider_ids,
    }


def _is_process_alive() -> bool:
    return _openclaw_process is not None and _openclaw_process.poll() is None


def _sanitize_command(command: list[str]) -> list[str]:
    sanitized: list[str] = []
    mask_next = False
    for part in command:
        if mask_next:
            sanitized.append("***")
            mask_next = False
            continue
        sanitized.append(part)
        if part in SENSITIVE_FLAGS:
            mask_next = True
    return sanitized


def _stop_managed_process(*, timeout: int = 10, kill_timeout: int = 5) -> int | None:
    global _openclaw_process

    if _openclaw_process is None or _openclaw_process.poll() is not None:
        _openclaw_process = None
        return None

    pid = _openclaw_process.pid
    _openclaw_process.terminate()
    try:
        _openclaw_process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        _openclaw_process.kill()
        _openclaw_process.wait(timeout=kill_timeout)

    _openclaw_process = None
    return pid


def _build_onboard_command(payload: OnboardRequest) -> list[str]:
    provider = ONBOARD_PROVIDER_MAP.get(payload.auth_choice)
    if provider is None:
        raise LauncherError(f"不支持的 auth_choice: {payload.auth_choice}")

    resolved_auth_choice = provider["auth_choice"]
    gateway_port, gateway_bind = _configured_gateway_settings()
    workspace = payload.workspace or str(config.default_workspace)

    command = [
        "onboard",
        "--non-interactive",
        "--accept-risk",
        "--mode",
        "local",
        "--flow",
        payload.flow,
        "--auth-choice",
        resolved_auth_choice,
        "--secret-input-mode",
        payload.secret_input_mode,
        "--workspace",
        workspace,
        "--gateway-port",
        str(payload.gateway_port or gateway_port),
        "--gateway-bind",
        payload.gateway_bind or gateway_bind,
    ]

    if payload.install_daemon:
        command.append("--install-daemon")
    else:
        command.append("--no-install-daemon")

    if payload.skip_channels:
        command.append("--skip-channels")
    if payload.skip_health:
        command.append("--skip-health")
    if payload.skip_search:
        command.append("--skip-search")
    if payload.skip_skills:
        command.append("--skip-skills")
    if payload.skip_ui:
        command.append("--skip-ui")

    api_key_flag = provider.get("api_key_flag")
    if provider["requires_api_key"] and not payload.api_key:
        raise LauncherError(f"{provider['label']} 需要填写 API Key")
    if api_key_flag and payload.api_key:
        command.extend([api_key_flag, payload.api_key])
    if not api_key_flag and payload.api_key:
        raise LauncherError(f"{provider['label']} 不接受 api_key 参数")

    if resolved_auth_choice == "custom-api-key":
        if not payload.custom_base_url:
            raise LauncherError("custom-api-key 需要 custom_base_url")
        if not payload.custom_model_id:
            raise LauncherError("custom-api-key 需要 custom_model_id")
        command.extend(
            [
                "--custom-base-url",
                payload.custom_base_url,
                "--custom-model-id",
                payload.custom_model_id,
                "--custom-compatibility",
                payload.custom_compatibility,
            ]
        )
        if payload.custom_provider_id:
            command.extend(["--custom-provider-id", payload.custom_provider_id])
    elif resolved_auth_choice == "ollama":
        if payload.custom_base_url:
            command.extend(["--custom-base-url", payload.custom_base_url])
        if payload.custom_model_id:
            command.extend(["--custom-model-id", payload.custom_model_id])
    elif any((payload.custom_base_url, payload.custom_model_id, payload.custom_provider_id)):
        raise LauncherError(f"{provider['label']} 不支持自定义 base_url/model_id/provider_id")

    return command


@app.get("/health")
async def health():
    return {"code": 200, "message": "ok"}


@app.get("/status")
async def status():
    """返回 OpenClaw 进程的当前状态。"""
    has_installed = detect_installed_command()
    has_state = detect_existing_state(config)
    configured = _read_config_summary()

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
            "configured": configured,
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
    global _openclaw_forward_args, _openclaw_process

    if _openclaw_process is not None and _openclaw_process.poll() is None:
        return {
            "code": 409,
            "message": "OpenClaw 已在运行中",
            "data": {"pid": _openclaw_process.pid},
        }

    try:
        forward_args = list(args) if args else list(config.default_args)
        _openclaw_process = launch(config, forward_args=forward_args)
        _openclaw_forward_args = forward_args
        return {
            "code": 200,
            "message": "OpenClaw 启动成功",
            "data": {
                "pid": _openclaw_process.pid if _openclaw_process else None,
                "args": forward_args,
            },
        }
    except LauncherError as exc:
        logger.error("启动 OpenClaw 失败: %s", exc)
        return {"code": 500, "message": f"启动失败: {exc}"}


@app.post("/stop")
async def stop_openclaw():
    """停止 OpenClaw 进程。"""
    pid = _stop_managed_process()
    if pid is None:
        return {"code": 200, "message": "OpenClaw 未在运行"}

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


@app.get("/onboard/options")
async def onboard_options():
    """返回可用于非交互 onboarding 的模型/供应商选项。"""
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "docs_url": ONBOARD_DOCS_URL,
            "providers": ONBOARD_PROVIDER_OPTIONS,
            "current": _read_config_summary(),
        },
    }


@app.post("/onboard")
async def onboard(payload: OnboardRequest):
    """使用官方 non-interactive onboarding 写入模型与认证配置。"""
    global _openclaw_process

    try:
        command = _build_onboard_command(payload)
        result = run_cli(command, config, ensure_state=True, timeout=300)
    except LauncherError as exc:
        logger.error("onboard 参数错误: %s", exc)
        return {"code": 400, "message": str(exc)}
    except subprocess.TimeoutExpired:
        logger.error("onboard 执行超时")
        return {"code": 500, "message": "onboard 执行超时"}

    if result is None:
        return {"code": 500, "message": "onboard 未执行"}

    if result.returncode != 0:
        logger.error("onboard 失败: stdout=%s stderr=%s", result.stdout, result.stderr)
        detail = (result.stderr or result.stdout or "未知错误").strip()
        return {
            "code": 500,
            "message": f"onboard 执行失败: {detail}",
            "data": {
                "command": _sanitize_command(["openclaw", *command]),
            },
        }

    restarted = False
    restart_pid = None
    was_running = _is_process_alive()
    if payload.restart_if_running and was_running:
        stopped_pid = _stop_managed_process()
        logger.info("onboard 完成后重启 OpenClaw, old_pid=%s", stopped_pid)
        try:
            forward_args = list(_openclaw_forward_args) if _openclaw_forward_args else list(config.default_args)
            _openclaw_process = launch(config, forward_args=forward_args)
            restart_pid = _openclaw_process.pid if _openclaw_process else None
            restarted = True
        except LauncherError as exc:
            logger.error("onboard 后重启失败: %s", exc)
            return {
                "code": 500,
                "message": f"配置已写入，但重启失败: {exc}",
                "data": {
                    "configured": _read_config_summary(),
                    "command": _sanitize_command(["openclaw", *command]),
                },
            }

    return {
        "code": 200,
        "message": "onboard 配置完成",
        "data": {
            "configured": _read_config_summary(),
            "restarted": restarted,
            "pid": restart_pid,
            "command": _sanitize_command(["openclaw", *command]),
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
        },
    }


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
    if _is_process_alive():
        logger.info("服务关闭，停止 OpenClaw 进程 pid=%s", _openclaw_process.pid)
        _stop_managed_process(timeout=5, kill_timeout=5)
