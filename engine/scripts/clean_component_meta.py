#!/usr/bin/env python3
"""Remove generated meta.json files from component directories."""

from pathlib import Path

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"


def clean_component_meta() -> int:
    """Delete meta.json files directly under engine/components/* directories."""
    removed = 0
    for meta_file in sorted(COMPONENTS_DIR.glob("*/meta.json")):
        if not meta_file.is_file():
            continue
        meta_file.unlink()
        removed += 1
        print(f"Removed {meta_file}")
    return removed


if __name__ == "__main__":
    count = clean_component_meta()
    print(f"Removed {count} component meta.json file(s).")
