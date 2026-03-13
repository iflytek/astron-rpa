from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OpenclawConfig:
    port: int = 8099
    host: str = "127.0.0.1"

    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent)
    source_root: Path = field(default=None)
    binary_root: Path = field(default=None)
    seed_root: Path = field(default=None)

    openclaw_home: Path = field(default=None)
    default_workspace: Path = field(default=None)
    config_path: Path = field(default=None)

    default_args: list[str] = field(default_factory=lambda: ["gateway"])

    def __post_init__(self):
        if self.source_root is None:
            self.source_root = self.project_root / "openclaw-src"
        if self.binary_root is None:
            self.binary_root = self.project_root / "binary"
        if self.seed_root is None:
            self.seed_root = self.project_root / ".openclaw-state.seed"
        if self.openclaw_home is None:
            self.openclaw_home = self.project_root / ".openclaw-state"
        if self.default_workspace is None:
            self.default_workspace = self.openclaw_home / "workspace"
        if self.config_path is None:
            self.config_path = self.openclaw_home / "openclaw.json"

    @property
    def bundled_node(self) -> Path:
        return self.binary_root / "node" / "node.exe"

    @property
    def bundled_pnpm(self) -> Path:
        return self.binary_root / "pnpm" / "pnpm.exe"


config = OpenclawConfig()
