#!/usr/bin/env python3
"""Launch the astron-rpa Engine scheduler and its managed services."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
RESOURCES_DIR = REPO_ROOT / "resources"
DEFAULT_CONF = RESOURCES_DIR / "conf.yaml"

RUN_MODES = {
    "dev": "Start the scheduler and all services managed by it.",
    "rpa-dev": "Alias for dev.",
    "scheduler": "Alias for dev.",
}


def resolve_conf(path: str) -> Path:
    conf = Path(path).expanduser().resolve()
    if not conf.is_file():
        raise FileNotFoundError(f"Configuration file does not exist: {conf}")
    return conf


def stop_engine_processes() -> None:
    """Stop Engine processes without waiting indefinitely on one stale process."""
    _terminate_processes(_find_engine_processes())


def _protected_process_ids() -> set[int]:
    """Return this launcher and its ancestors, which must never be terminated."""
    import psutil

    protected: set[int] = set()
    try:
        process = psutil.Process(os.getpid())
        while process:
            protected.add(process.pid)
            process = process.parent()
    except psutil.Error:
        protected.add(os.getpid())
    return protected


def _find_engine_processes() -> list:
    """Find Engine executables, including children re-parented after shutdown."""
    import psutil

    protected = _protected_process_ids()
    processes = []
    for process in psutil.process_iter(["pid", "exe"]):
        if process.pid in protected:
            continue
        try:
            executable = (process.info.get("exe") or "").lower()
        except psutil.Error:
            continue
        if "astron-rpa" in executable:
            processes.append(process)
    return processes


def _terminate_processes(processes: list) -> int:
    """Terminate processes with a bounded Windows command and return the count."""
    import psutil

    unique_processes = {process.pid: process for process in processes}
    if sys.platform == "win32":
        for process in unique_processes.values():
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
    else:
        for process in unique_processes.values():
            try:
                process.kill()
            except psutil.Error:
                pass
        if unique_processes:
            psutil.wait_procs(list(unique_processes.values()), timeout=5)
    return len(unique_processes)


def run_scheduler(conf: Path) -> int:
    sys.stdout.write(f"[dev] Starting scheduler in launcher: {sys.executable} -m astronverse.scheduler --conf {conf}\n")
    try:
        from astronverse.scheduler.start import start

        start(argparse.Namespace(conf=str(conf), venv=None, stop=False))
    except KeyboardInterrupt:
        sys.stdout.write("\n[dev] Stopping scheduler...\n")
        return 0
    finally:
        sys.stdout.write("[dev] Scheduler stopped.\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    modes = ", ".join(RUN_MODES)
    parser = argparse.ArgumentParser(
        prog="uv run scripts/start.py",
        description="AstronRPA Engine launcher for the scheduler-managed architecture.",
        epilog=(
            f"modes: {modes}\n"
            "examples:\n"
            "  uv run scripts/start.py dev\n"
            "  uv run scripts/start.py dev --conf ../resources/conf.local.yaml\n"
            "  uv run scripts/start.py stop"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("mode", choices=[*RUN_MODES, "stop"], help="run mode or stop")
    parser.add_argument(
        "--conf",
        type=Path,
        default=DEFAULT_CONF,
        help=f"scheduler configuration file (default: {DEFAULT_CONF})",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.mode == "stop":
        stop_engine_processes()
        sys.stdout.write("[dev] Engine processes stopped.\n")
        return 0

    try:
        conf = resolve_conf(str(args.conf))
    except FileNotFoundError as exc:
        sys.stderr.write(f"[dev] {exc}\n")
        return 1

    return run_scheduler(conf)


if __name__ == "__main__":
    raise SystemExit(main())
