from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _default_package_root() -> Path:
    return Path(__file__).resolve().parent


def _is_source_checkout(project_root: Path) -> bool:
    return (project_root / "pyproject.toml").is_file()


def _default_openclaw_home(*, packaged: bool, project_root: Path) -> Path:
    if not packaged:
        return project_root / ".openclaw-state"

    if os.name == "nt":
        base_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    else:
        base_dir = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))

    return base_dir / "astronverse-openclaw" / ".openclaw-state"


@dataclass
class OpenclawConfig:
    port: int = 8099
    host: str = "127.0.0.1"

    project_root: Path = field(default_factory=_default_project_root)
    package_root: Path = field(default_factory=_default_package_root)
    source_root: Path = field(default=None)
    binary_root: Path = field(default=None)
    seed_root: Path = field(default=None)

    openclaw_home: Path = field(default=None)
    default_workspace: Path = field(default=None)
    config_path: Path = field(default=None)

    default_args: list[str] = field(default_factory=lambda: ["gateway"])

    def __post_init__(self):
        packaged = not _is_source_checkout(self.project_root)

        if self.source_root is None:
            self.source_root = self.package_root / "openclaw-src"
        if self.binary_root is None:
            self.binary_root = self.package_root / "binary"
        if self.seed_root is None:
            self.seed_root = self.package_root / ".openclaw-state.seed"
        if self.openclaw_home is None:
            self.openclaw_home = _default_openclaw_home(
                packaged=packaged,
                project_root=self.project_root,
            )
        if self.default_workspace is None:
            self.default_workspace = self.openclaw_home / "workspace"
        if self.config_path is None:
            self.config_path = self.openclaw_home / "openclaw.json"

    @property
    def bundled_node(self) -> Path:
        return self.binary_root / "node" / "node.exe"

    @property
    def bundled_npm(self) -> Path:
        return self.binary_root / "node" / "npm.cmd"

    @property
    def bundled_npx(self) -> Path:
        return self.binary_root / "node" / "npx.cmd"

    @property
    def bundled_pnpm(self) -> Path:
        return self.binary_root / "pnpm" / "pnpm.exe"

    @property
    def runtime_shim_root(self) -> Path:
        return self.openclaw_home / ".runtime-shims"


config = OpenclawConfig()
