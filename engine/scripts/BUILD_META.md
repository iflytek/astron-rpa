[中文](BUILD_META.zh.md) | English
# build_meta.py Script Reference

`build_meta.py` runs as a uv script under `engine` to build and merge component meta and tree configs.

## Overview

- Component list is managed entirely by `engine/pyproject.toml` — no manual maintenance needed
- **Platform-aware build**: output only contains atomics supported on the current platform; each platform produces an independent artifact
- Runs each component's `meta.py` to generate/update multi-locale resources
- Merges all component `meta.json` files, sorted by key
- Deep-merges all component `tree.json` files with built-in type definitions
- Supports `zh_CN` and `en_US` locales

## Setup

The script must be run from the `engine` root via [uv](https://docs.astral.sh/uv/).

1. Install uv (skip if already installed):
  ```bash
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
2. Sync dependencies and run:
  ```bash
  cd engine
  uv sync
  uv run scripts/build_meta.py
  ```

## Build Flow

1. **Load component list**  
   Reads `engine/pyproject.toml` `[tool.uv.sources]` and collects all entries whose `path` contains `components/`. Adding or removing a component only requires editing `pyproject.toml`.

2. **Run component meta.py**  
   Iterates the component list and executes each component's `meta.py`, generating/updating `resources/{locale}/meta.json`, `tree.json`, and `meta_type.json`. A failed component is skipped and logged without blocking others.

3. **Build per locale** (`zh_CN` and `en_US`):

   a. **Merge meta.json (with platform filtering)**  
     Aggregates all component `resources/{locale}/meta.json` files. Atomics whose `platform` field does not match the current `sys.platform` are dropped. The `platform` field is stripped from the output.

   b. **Merge meta_type.json**  
     Merges all component `resources/{locale}/meta_type.json` type definitions.

   c. **Merge tree.json**  
     Deep-merges all component `resources/{locale}/tree.json` files into `temp_local_tree.json`. Nodes with the same key are merged recursively through their `atomics` children.

   d. **Build final meta**  
     Sorts the merged meta by `atomKey` and writes to `resources/meta/{locale}/meta.json`.

   e. **Build final tree**  
     Merges the tree with built-in type config from `astronverse-actionlib` (`get_types_config` / `get_common_advanced_parameters`). Built-in types take precedence over component-registered types. Output: `resources/meta/{locale}/tree.json`.

## Platform Support

Build artifacts are platform-specific. Each platform builds independently and the output contains no `platform` field.

### 1. Package-level restriction

Declared via Python Environment Markers in `engine/pyproject.toml`, enforced by `uv` at install time:

```toml
dependencies = [
    # All platforms
    "astronverse-system",
    "astronverse-browser",

    # Windows only
    "astronverse-word; sys_platform == 'win32'",
    "astronverse-winelement; sys_platform == 'win32'",
]
```

On macOS/Linux, `uv sync` skips packages marked `sys_platform == 'win32'`. The build script also reads both `[project.dependencies]` (for platform markers) and `[tool.uv.sources]` (for paths) when loading the component list, and automatically skips components not supported on the current platform.

### 2. Atomic-level restriction

For atomics within a component that only run on certain platforms, declare `platform` in the decorator (values match `sys.platform`):

```python
# All platforms (default — omit platform)
@atomicMg.atomic()
def list_processes(self):
    pass

# Windows only
@atomicMg.atomic(platform="win32")
def get_window_handle(self, pid: int):
    pass

# Multiple platforms (comma-separated)
@atomicMg.atomic(platform="win32,darwin")
def get_clipboard_text(self):
    pass
```

Atomics whose `platform` does not match the current `sys.platform` are filtered out during the merge step and do not appear in the output.

**Platform identifiers (match `sys.platform`):**
- `win32` — Windows
- `darwin` — macOS
- `linux` — Linux

## Output Files

| File | Description |
|------|-------------|
| `engine/scripts/temp_local_meta.json` | Intermediate merged meta (last locale) |
| `engine/scripts/temp_local_tree.json` | Intermediate merged tree (last locale) |
| `resources/meta/zh_CN/meta.json` | Final meta config (Chinese) |
| `resources/meta/zh_CN/tree.json` | Final tree config (Chinese) |
| `resources/meta/en_US/meta.json` | Final meta config (English) |
| `resources/meta/en_US/tree.json` | Final tree config (English) |

## Notes

- Built-in type definitions from `astronverse-actionlib` (`get_types_config`, `get_common_advanced_parameters`) take precedence over component-registered types.
- If a component's `meta.py` fails, that component is skipped without affecting others.
