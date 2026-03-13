"""
OpenClaw launcher – manages detecting, installing, syncing, and running OpenClaw.

Refactored from the original ``openclaw_launcher.py`` into a reusable module
that is driven by the FastAPI service layer.
"""

from __future__ import annotations

import filecmp
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from astronverse.openclaw.config import OpenclawConfig, config as default_config

logger = logging.getLogger("astronverse.openclaw")

BACKUP_SUFFIX = ".launcher.bak"

INSTALL_STEPS = ("install", "ui:build", "build")


class LauncherError(RuntimeError):
    """Raised when the launcher cannot build a runnable command."""


@dataclass(frozen=True)
class SyncRule:
    source_names: tuple[str, ...]
    destination: Path


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
    return shutil.which("pnpm")


def _has_bundled_source_runtime(cfg: OpenclawConfig) -> bool:
    # if _resolve_pnpm_command(cfg) is None:
    #     return False
    # if not (cfg.source_root / "package.json").is_file():
    #     return False
    # if not (cfg.source_root / "scripts" / "run-node.mjs").is_file():
    #     return False
    # return (cfg.source_root / "node_modules").is_dir()
    return True


def _find_git_bash_bin() -> str | None:
    """Locate Git-for-Windows ``bin`` dir so its ``bash`` takes priority over WSL."""
    git = shutil.which("git")
    if not git:
        return None
    git_bin = Path(git).resolve().parent.parent / "bin"
    if (git_bin / "bash.exe").is_file():
        return str(git_bin)
    return None


def build_env(cfg: OpenclawConfig) -> dict[str, str]:
    env = os.environ.copy()

    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    current_path = env.get(path_key, "")

    extra_dirs: list[str] = []
    for candidate in (cfg.bundled_node.parent, cfg.bundled_pnpm.parent):
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

    env["OPENCLAW_HOME"] = str(cfg.project_root)
    env["OPENCLAW_STATE_DIR"] = str(cfg.openclaw_home)
    env["OPENCLAW_CONFIG_PATH"] = str(cfg.config_path)

    return env


def _find_prepared_file(cfg: OpenclawConfig, candidates: tuple[str, ...]) -> Path | None:
    for root in (cfg.project_root, cfg.seed_root, cfg.seed_root / "workspace"):
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
    if not cfg.source_root.exists():
        raise LauncherError(f"source directory not found: {cfg.source_root}")

    pnpm_command = _resolve_pnpm_command(cfg)
    if pnpm_command is None:
        raise LauncherError(
            "cannot build OpenClaw from source because `pnpm` is unavailable.\n"
            "Provide bundled `binary/pnpm`, install `pnpm`, or ship prebuilt `openclaw-src/dist`."
        )

    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    logger.info("install_from_source PATH[%s]=%s", path_key, env.get(path_key, "<unset>"))

    changes: list[str] = []
    for label in INSTALL_STEPS:
        command = [pnpm_command, label]
        changes.append(f"run {label}: {' '.join(command)}")
        if dry_run:
            continue
        completed = subprocess.run(command, cwd=str(cfg.source_root), env=env)
        if completed.returncode != 0:
            raise LauncherError(f"source install step failed: {label}")
    return changes


def resolve_command(cfg: OpenclawConfig, forward_args: list[str]) -> tuple[list[str], str]:
    """Return (command, mode) where mode is 'bundled', 'installed', or 'source'."""
    pnpm = _resolve_pnpm_command(cfg)
    if pnpm and _has_bundled_source_runtime(cfg):
        return [pnpm, "openclaw", *forward_args], "bundled"

    installed = shutil.which("openclaw")
    if installed:
        return [installed, *forward_args], "installed"

    if not cfg.source_root.exists():
        raise LauncherError(f"source directory not found: {cfg.source_root}")

    if pnpm:
        return [pnpm, "openclaw", *forward_args], "source"

    node = _resolve_node_command(cfg)
    node_modules = cfg.source_root / "node_modules"
    if node and node_modules.exists():
        return [node, "scripts/run-node.mjs", *forward_args], "source"

    raise LauncherError(
        "cannot find a runnable OpenClaw backend.\n"
        "Expected one of:\n"
        "1. bundled `pnpm openclaw` runtime in `openclaw-src`\n"
        "2. an `openclaw` command in PATH\n"
        "3. `pnpm` available for `openclaw-src`\n"
        "4. `node` plus `openclaw-src/node_modules`"
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

    has_bundled = _has_bundled_source_runtime(cfg)
    has_installed = detect_installed_command()
    has_state = detect_existing_state(cfg)
    env = build_env(cfg)

    install_changes: list[str] = []
    sync_changes: list[str] = []

    if not has_bundled and not has_installed:
        install_changes = install_from_source(cfg, env, dry_run=dry_run)
        has_bundled = _has_bundled_source_runtime(cfg)

    if not has_state:
        sync_changes = sync_prepared_files(cfg, dry_run=dry_run)

    command, mode = resolve_command(cfg, forward_args)
    cwd = None if mode == "installed" else str(cfg.source_root)

    logger.info("bundled_runtime=%s", has_bundled)
    logger.info("installed_command=%s", has_installed)
    logger.info("existing_state=%s", has_state)
    logger.info("openclaw_home=%s", cfg.openclaw_home)
    logger.info("workspace=%s", cfg.default_workspace)
    for c in install_changes:
        logger.info("install=%s", c)
    for c in sync_changes:
        logger.info("sync=%s", c)
    logger.info("mode=%s", mode)
    logger.info("command=%s", " ".join(command))

    if dry_run:
        return None

    return subprocess.Popen(command, env=env, cwd=cwd)
