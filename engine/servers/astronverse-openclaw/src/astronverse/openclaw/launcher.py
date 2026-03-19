"""
OpenClaw launcher – manages detecting, installing, syncing, and running OpenClaw.

Refactored from the original ``openclaw_launcher.py`` into a reusable module
that is driven by the FastAPI service layer.
"""

from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from astronverse.openclaw.config import OpenclawConfig
from astronverse.openclaw.config import config as default_config
from astronverse.openclaw.logger import logger

BACKUP_SUFFIX = ".launcher.bak"


class LauncherError(RuntimeError):
    """Raised when the launcher cannot build a runnable command."""


@dataclass(frozen=True)
class SyncRule:
    source_names: tuple[str, ...]
    destination: Path


@dataclass(frozen=True)
class PreparedCommand:
    command: list[str]
    env: dict[str, str]
    cwd: str | None
    mode: str
    install_changes: list[str]
    sync_changes: list[str]


def _build_sync_rules(cfg: OpenclawConfig) -> tuple[SyncRule, ...]:
    ws = cfg.default_workspace
    return (
        SyncRule(("openclaw.json",), cfg.config_path),
        SyncRule(("AGENTS.md", "AGENTS.MD"), ws / "AGENTS.md"),
        SyncRule(("SOUL.md", "SOUL.MD"), ws / "SOUL.md"),
        SyncRule(("TOOLS.md", "TOOLS.MD"), ws / "TOOLS.md"),
        SyncRule(("IDENTITY.md", "IDENTITY.MD"), ws / "IDENTITY.md"),
        SyncRule(("USER.md", "USER.MD"), ws / "USER.md"),
        SyncRule(("HEARTBEAT.md", "HEARTBEAT.MD"), ws / "HEARTBEAT.md"),
        SyncRule(("BOOTSTRAP.md", "BOOTSTRAP.MD"), ws / "BOOTSTRAP.md"),
        SyncRule(("MEMORY.md", "MEMORY.MD", "memory.md"), ws / "MEMORY.md"),
    )


def detect_existing_state(cfg: OpenclawConfig) -> bool:
    return cfg.config_path.exists()


def detect_installed_command() -> bool:
    return shutil.which("openclaw") is not None


def _resolve_node_command(cfg: OpenclawConfig) -> str | None:
    if cfg.bundled_node.exists():
        return str(cfg.bundled_node)
    return shutil.which("node")


def _resolve_pnpm_command(cfg: OpenclawConfig) -> str | None:
    if cfg.bundled_pnpm.exists():
        return str(cfg.bundled_pnpm)
    return None


def _resolve_source_openclaw_command(cfg: OpenclawConfig) -> list[str] | None:
    bin_dir = cfg.source_root / "node_modules" / ".bin"
    local_cli = bin_dir / ("openclaw.cmd" if os.name == "nt" else "openclaw")
    if local_cli.is_file():
        return [str(local_cli)]

    node = _resolve_node_command(cfg)
    local_entry = cfg.source_root / "node_modules" / "openclaw" / "openclaw.mjs"
    if node and local_entry.is_file():
        return [node, str(local_entry)]

    return None


def _has_bundled_source_runtime(cfg: OpenclawConfig) -> bool:
    return _resolve_source_openclaw_command(cfg) is not None


def _is_source_root_empty(cfg: OpenclawConfig) -> bool:
    if not cfg.source_root.exists():
        return True

    return not any(cfg.source_root.iterdir())


def _find_git_bash_bin() -> str | None:
    """Locate Git-for-Windows ``bin`` dir so its ``bash`` takes priority over WSL."""
    git = shutil.which("git")
    if not git:
        return None
    git_bin = Path(git).resolve().parent.parent / "bin"
    if (git_bin / "bash.exe").is_file():
        return str(git_bin)
    return None


def _write_text_if_changed(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def ensure_runtime_shims(cfg: OpenclawConfig) -> list[str]:
    shim_root = cfg.runtime_shim_root
    shim_root.mkdir(parents=True, exist_ok=True)

    changes: list[str] = []
    if os.name == "nt":
        wrappers = {
            "node.cmd": f'@echo off\r\n"{cfg.bundled_node}" %*\r\n',
            "npm.cmd": f'@echo off\r\n"{cfg.bundled_npm}" %*\r\n',
            "npx.cmd": f'@echo off\r\n"{cfg.bundled_npx}" %*\r\n',
            "pnpm.cmd": f'@echo off\r\n"{cfg.bundled_pnpm}" %*\r\n',
        }
    else:
        wrappers = {
            "node": f'#!/usr/bin/env sh\nexec "{cfg.bundled_node}" "$@"\n',
            "npm": f'#!/usr/bin/env sh\nexec "{cfg.bundled_npm}" "$@"\n',
            "npx": f'#!/usr/bin/env sh\nexec "{cfg.bundled_npx}" "$@"\n',
            "pnpm": f'#!/usr/bin/env sh\nexec "{cfg.bundled_pnpm}" "$@"\n',
        }

    for name, content in wrappers.items():
        target = shim_root / name
        before_exists = target.exists()
        _write_text_if_changed(target, content)
        if os.name != "nt":
          target.chmod(0o755)
        changes.append(f"{'update' if before_exists else 'create'} shim {target}")

    return changes


def build_env(cfg: OpenclawConfig) -> dict[str, str]:
    env = os.environ.copy()
    shim_changes = ensure_runtime_shims(cfg)

    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    current_path = env.get(path_key, "")

    extra_dirs: list[str] = []
    for candidate in (cfg.runtime_shim_root, cfg.bundled_node.parent, cfg.bundled_pnpm.parent):
        d = str(candidate)
        if candidate.is_dir() and d not in extra_dirs:
            extra_dirs.append(d)

    if os.name == "nt":
        git_bash_bin = _find_git_bash_bin()
        if git_bash_bin and git_bash_bin not in extra_dirs:
            extra_dirs.append(git_bash_bin)

    if extra_dirs:
        prefix = os.pathsep.join(extra_dirs)
        env[path_key] = f"{prefix}{os.pathsep}{current_path}" if current_path else prefix

    env["OPENCLAW_HOME"] = str(cfg.openclaw_home)
    env["OPENCLAW_STATE_DIR"] = str(cfg.openclaw_home)
    env["OPENCLAW_CONFIG_PATH"] = str(cfg.config_path)
    env["OPENCLAW_MANAGED_NODE"] = str(cfg.bundled_node)
    env["OPENCLAW_MANAGED_NPM"] = str(cfg.bundled_npm)
    env["OPENCLAW_MANAGED_NPX"] = str(cfg.bundled_npx)
    env["OPENCLAW_MANAGED_PNPM"] = str(cfg.bundled_pnpm)

    for change in shim_changes:
        logger.info("runtime={}", change)

    return env


def _find_prepared_file(cfg: OpenclawConfig, candidates: tuple[str, ...]) -> Path | None:
    for root in (cfg.package_root, cfg.seed_root, cfg.seed_root / "workspace"):
        for name in candidates:
            candidate = root / name
            if candidate.exists() and candidate.is_file():
                return candidate
    return None


def ensure_seed_state(cfg: OpenclawConfig, *, dry_run: bool = False) -> list[str]:
    if not cfg.seed_root.exists():
        return []
    if cfg.config_path.exists():
        return []

    changes = [f"seed {cfg.seed_root} -> {cfg.openclaw_home}"]
    if not dry_run:
        shutil.copytree(cfg.seed_root, cfg.openclaw_home, dirs_exist_ok=True)
    return changes


def sync_prepared_files(cfg: OpenclawConfig, *, dry_run: bool = False) -> list[str]:
    changes = ensure_seed_state(cfg, dry_run=dry_run)
    if not dry_run:
        cfg.openclaw_home.mkdir(parents=True, exist_ok=True)
        cfg.default_workspace.mkdir(parents=True, exist_ok=True)

    for rule in _build_sync_rules(cfg):
        source = _find_prepared_file(cfg, rule.source_names)
        if source is None:
            continue

        destination = rule.destination
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            if filecmp.cmp(source, destination, shallow=False):
                changes.append(f"unchanged {destination}")
                continue
            backup = destination.with_name(destination.name + BACKUP_SUFFIX)
            changes.append(f"backup {destination} -> {backup}")
            changes.append(f"update {source} -> {destination}")
            if not dry_run:
                shutil.copy2(destination, backup)
                shutil.copy2(source, destination)
            continue

        changes.append(f"copy {source} -> {destination}")
        if not dry_run:
            shutil.copy2(source, destination)

    return changes


def install_from_source(cfg: OpenclawConfig, env: dict[str, str], *, dry_run: bool = False) -> list[str]:
    pnpm_command = _resolve_pnpm_command(cfg)
    if pnpm_command is None:
        raise LauncherError(
            "cannot install OpenClaw into openclaw-src because bundled pnpm is unavailable.\n"
            "Expected bundled `binary/pnpm/pnpm.exe`."
        )

    package_json = cfg.source_root / "package.json"
    if not _is_source_root_empty(cfg) and package_json.exists():
        logger.info("skip source bootstrap install because package.json already exists: {}", package_json)
        return []

    bootstrap_command = [pnpm_command, "install", "openclaw"]

    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    logger.info("install_from_source PATH[{}]={}", path_key, env.get(path_key, "<unset>"))

    changes = [f"run bootstrap install: {' '.join(bootstrap_command)}"]
    if dry_run:
        return changes

    cfg.source_root.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(bootstrap_command, cwd=str(cfg.source_root), env=env)
    if completed.returncode != 0:
        raise LauncherError("source bootstrap install failed")

    if not _has_bundled_source_runtime(cfg):
        raise LauncherError("source bootstrap completed but local openclaw CLI was not created")

    return changes


def resolve_command(cfg: OpenclawConfig, forward_args: list[str]) -> tuple[list[str], str]:
    """Return (command, mode) where mode is 'bundled', 'installed', or 'source'."""
    bundled = _resolve_source_openclaw_command(cfg)
    if bundled:
        return [*bundled, *forward_args], "bundled"

    if not cfg.source_root.exists():
        raise LauncherError(f"source directory not found: {cfg.source_root}")

    raise LauncherError(
        "cannot find a runnable OpenClaw backend.\n"
        "Expected one of:\n"
        "1. local `openclaw-src/node_modules/.bin/openclaw`\n"
        "2. local `openclaw-src/node_modules/openclaw/openclaw.mjs`"
    )


def _mask_command(command: list[str]) -> list[str]:
    masked: list[str] = []
    mask_next = False
    for part in command:
        if mask_next:
            masked.append("***")
            mask_next = False
            continue
        masked.append(part)
        if part.startswith("--") and any(token in part for token in ("api-key", "token", "password")):
            mask_next = True
    return masked


def prepare_command(
    cfg: OpenclawConfig | None = None,
    forward_args: list[str] | None = None,
    *,
    ensure_state: bool = False,
    dry_run: bool = False,
) -> PreparedCommand:
    if cfg is None:
        cfg = default_config
    if forward_args is None:
        forward_args = []

    has_bundled = _has_bundled_source_runtime(cfg)
    has_state = detect_existing_state(cfg)
    env = build_env(cfg)

    install_changes: list[str] = []
    sync_changes: list[str] = []

    if not has_bundled:
        install_changes = install_from_source(cfg, env, dry_run=dry_run)

    if ensure_state and not has_state:
        sync_changes = sync_prepared_files(cfg, dry_run=dry_run)

    command, mode = resolve_command(cfg, forward_args)
    cwd = None if mode == "installed" else str(cfg.source_root)

    return PreparedCommand(
        command=command,
        env=env,
        cwd=cwd,
        mode=mode,
        install_changes=install_changes,
        sync_changes=sync_changes,
    )


def run_cli(
    forward_args: list[str],
    cfg: OpenclawConfig | None = None,
    *,
    ensure_state: bool = False,
    dry_run: bool = False,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str] | None:
    prepared = prepare_command(
        cfg,
        forward_args,
        ensure_state=ensure_state,
        dry_run=dry_run,
    )

    logger.info("mode={}", prepared.mode)
    logger.info("command={}", " ".join(_mask_command(prepared.command)))
    for c in prepared.install_changes:
        logger.info("install={}", c)
    for c in prepared.sync_changes:
        logger.info("sync={}", c)

    if dry_run:
        return None

    return subprocess.run(
        prepared.command,
        env=prepared.env,
        cwd=prepared.cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def launch(
    cfg: OpenclawConfig | None = None,
    forward_args: list[str] | None = None,
    *,
    dry_run: bool = False,
) -> subprocess.Popen | None:
    """
    Detect, install, sync, and launch OpenClaw.

    Returns a ``Popen`` handle for the running process (or ``None`` on dry-run).
    """
    if cfg is None:
        cfg = default_config
    if forward_args is None:
        forward_args = list(cfg.default_args)

    prepared = prepare_command(
        cfg,
        forward_args,
        ensure_state=True,
        dry_run=dry_run,
    )

    logger.info("bundled_runtime={}", _has_bundled_source_runtime(cfg))
    logger.info("existing_state={}", detect_existing_state(cfg))
    logger.info("openclaw_home={}", cfg.openclaw_home)
    logger.info("workspace={}", cfg.default_workspace)
    for c in prepared.install_changes:
        logger.info("install={}", c)
    for c in prepared.sync_changes:
        logger.info("sync={}", c)
    logger.info("mode={}", prepared.mode)
    logger.info("command={}", " ".join(_mask_command(prepared.command)))

    if dry_run:
        return None

    return subprocess.Popen(prepared.command, env=prepared.env, cwd=prepared.cwd)
