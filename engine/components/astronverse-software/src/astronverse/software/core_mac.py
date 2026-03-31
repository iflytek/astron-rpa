import os
import subprocess
from pathlib import Path

from astronverse.software.core import ISoftwareCore


class SoftwareCore(ISoftwareCore):
    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        if not app_name:
            return ""

        return (
            SoftwareCore._find_by_direct_path(app_name)
            or SoftwareCore._find_in_common_app_dirs(app_name)
            or SoftwareCore._find_by_mdfind(app_name)
        )

    @staticmethod
    def _find_by_direct_path(app_name: str) -> str:
        candidate = Path(app_name).expanduser()
        if candidate.exists():
            return str(candidate)
        return ""

    @staticmethod
    def _find_in_common_app_dirs(app_name: str) -> str:
        for candidate_name in SoftwareCore._candidate_app_names(app_name):
            for app_dir in SoftwareCore._app_search_dirs():
                candidate = app_dir / candidate_name
                if candidate.exists():
                    return str(candidate)
        return ""

    @staticmethod
    def _find_by_mdfind(app_name: str) -> str:
        # Keep Spotlight lookup isolated so it can be refined after macOS
        # validation without touching the rest of the module contract.
        try:
            result = subprocess.run(
                ["mdfind", f'kMDItemKind == "Application" && kMDItemFSName == "{app_name}"c'],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            return ""

        for line in result.stdout.splitlines():
            candidate = line.strip()
            if candidate and os.path.exists(candidate):
                return candidate
        return ""

    @staticmethod
    def _app_search_dirs() -> list[Path]:
        return [
            Path("/Applications"),
            Path.home() / "Applications",
        ]

    @staticmethod
    def _candidate_app_names(app_name: str) -> list[str]:
        normalized_name = app_name.strip()
        if not normalized_name:
            return []
        if normalized_name.endswith(".app"):
            return [normalized_name]
        return [normalized_name, f"{normalized_name}.app"]
