English | [简体中文](DEVELOP.zh.md)
# Engine Development Guide

This document is intended for engine module developers. It explains how to develop atomic capability components and how to perform end-to-end debugging.

---

## Directory Structure

```
engine/
├── components/          # Atomic capability components (each subdirectory is an independent Python package)
│   ├── astronverse-browser/
│   ├── astronverse-excel/
│   └── ...
├── shared/              # Shared base libraries
│   ├── astronverse-actionlib/   # Atomic capability registration framework
│   ├── astronverse-workflowlib/ # Workflow execution library
│   └── ...
├── main.py              # Debug startup entry (includes meta build)
├── meta_build.py        # Meta/tree configuration build script
└── pyproject.toml       # Project dependency declarations
```

---

## Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) to manage the Python environment and dependencies.

1. Install uv (skip if already installed):
  ```bash
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

2. Sync dependencies in the `engine` directory:
  ```bash
  cd engine
  uv sync
  ```

---

## Developing Atomic Capability Components

### Component Directory Structure

Each component is an independent editable Python package with the following structure:

```
components/astronverse-browser/
├── src/
│   └── astronverse/
│       └── browser/
│           ├── browser_software.py   # Atomic capability implementation
│           └── ...
├── config.yaml          # Atomic capability UI config (title, icon, param descriptions, tree path)
├── config_type.yaml     # Type definition config
├── meta.py              # Meta/tree generation entry point
├── meta.json            # Generated meta output (do not edit manually)
├── tree.json            # Generated tree output (do not edit manually)
├── meta_type.json       # Generated type output (do not edit manually)
└── pyproject.toml       # Component dependency declarations
```

### Implementing an Atomic Capability

In the component's `src` directory, register atomic capabilities with the `@atomicMg.atomic()` decorator:

```python
from astronverse.actionlib.atomic import atomicMg

class BrowserSoftware:
    @atomicMg.atomic()
    def browser_open(self, url: str, browser_type: str = "chrome") -> object:
        # Implementation
        ...
```

- The class name is used as `group_key`; the generated `key` follows the format `ClassName.method_name`
- Parameter type annotations are automatically mapped to frontend form control types
- Return values must be declared in `config.yaml` under `outputList`

### Configuring config.yaml

```yaml
atomic:
  BrowserSoftware.browser_open:
    title: Open Browser
    icon: open-browser
    comment: Open @{browser_type} and navigate to @{url}, output @{web_open}
    helpManual: ''
    path:
      - /atomicTree/web        # Mount path in the tree, must follow /path1/path2/... format
    inputList:
      - key: url
        title: Initial URL
        tip: Enter the URL to open
    outputList:
      - key: web_open
        title: Browser Object
```

- `path` supports multiple entries; the atomic capability will appear under multiple tree nodes simultaneously
- All `@{key}` references in `comment` must have a corresponding entry in `inputList` or `outputList`

### Registering in meta.py

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg

if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(BrowserSoftware, version=get_version())
    atomicMg.meta()                                          # Generates meta.json

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")                                 # Generates tree.json
```

### Generating Meta for a Single Component

```bash
cd engine/components/astronverse-browser
uv run meta.py
```

### Generating Meta for All Components and Merging

```bash
cd engine
uv run meta_build.py
```

Output:
- `resources/meta/meta.json` — Full atomic capability configuration
- `resources/meta/tree.json` — Full tree configuration

---

## End-to-End Debugging

### Debug Entry Point

`main.py` is the dedicated debug entry point. On startup it:
1. Calls `MetaBuilder` to rebuild the full meta/tree configuration
2. Starts the scheduler and establishes a WebSocket connection with the frontend

```bash
cd engine
uv run main.py
```
3. Check the started route_port, which is the port used by the client to connect to the engine service.
```bash
route_port=13159
```

### Configuring the Debug Environment

Modify the `/resources/config.yaml` file in the project root and set `skip_engine_start` to `true` to skip starting the Engine from the client. (This will cause inter-process communication to be disabled, but it does not affect debugging.)
Note: When building the installation package, `skip_engine_start` should be set to `false`.

### Frontend Integration Debugging

The frontend (Electron desktop app) controls the engine process lifecycle via `server.ts`:

- In development mode, the frontend sets `config.skip_engine_start = true` to skip launching the engine process and connects directly to a locally running engine instance
- The engine defaults to port `13160`, which can be overridden via the `PORT` environment variable
- After startup, the engine pushes events to the frontend via stdout messages prefixed with `||emit||`

Steps for frontend + backend joint debugging:

1. Start the engine first:
   ```bash
   cd engine
   uv run main.py
   ```
2. Start the frontend dev server:
   ```bash
   cd frontend
   set PORT={route_port} && pnpm dev:desktop
   ```

### Debugging a Single Component

You can run a specific module or tests directly within a component:

```bash
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

---

## Code Standards

- Code formatting uses `ruff`; see `.ruff.toml` for configuration
- The `path` field in atomic capability config must follow the `/path1/path2/...` format; a validation error will be thrown at build time otherwise
- Generated files (`meta.json`, `tree.json`, etc.) must not be edited manually — regenerate them by running `meta.py`

---

If you have any questions, please contact the project maintainer.
