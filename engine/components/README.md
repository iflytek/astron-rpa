[简体中文](README.zh.md) | English

# Components Development Guide

This document is intended for developers of the components module and explains how to develop atomic capability components and perform debugging.

---

## Table of Contents

- [Environment Setup](#environment-setup)
- [Developing Atomic Capability Components](#developing-atomic-capability-components)
- [End-to-End Debugging](#end-to-end-debugging)
- [Code Standards](#code-standards)

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
├── config.yaml          # Atomic capability UI configuration (title, icon, parameter descriptions, tree path)
├── config_type.yaml     # Type definition configuration
├── meta.py              # meta/tree generation entry point
├── meta.json            # Generated meta output (do not edit manually)
├── tree.json            # Generated tree output (do not edit manually)
├── meta_type.json       # Generated type output (do not edit manually)
└── pyproject.toml       # Component dependency declaration
```

### Implementing an Atomic Capability

In the component's `src` directory, register atomic capabilities using the `@atomicMg.atomic()` decorator:

```python
from astronverse.actionlib.atomic import atomicMg

class BrowserSoftware:
    @atomicMg.atomic()
    def browser_open(self, url: str, browser_type: str = "chrome") -> object:
        # Implementation logic
        ...
```

- The class name serves as the `group_key`; the generated `key` format is `ClassName.method_name`.
- Parameter type annotations are automatically mapped to frontend form control types.
- Return values must be declared in the `outputList` of `config.yaml`.

### Configuring config.yaml

```yaml
atomic:
  BrowserSoftware.browser_open:
    title: Open Browser
    icon: open-browser
    comment: Open @{browser_type} and navigate to @{url}, output @{web_open}
    helpManual: ''
    path:
      - /atomicTree/web        # Mount path in the tree, must follow the /path1/path2/... format
    inputList:
      - key: url
        title: Initial URL
        tip: Enter the URL to open
    outputList:
      - key: web_open
        title: Browser Object
```

- `path` supports multiple entries; the atomic capability will appear under multiple tree nodes simultaneously.
- `@{key}` references in `comment` must correspond to definitions in `inputList` or `outputList`.

### Registering in meta.py

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg

if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(BrowserSoftware, version=get_version())
    atomicMg.meta()                                          # Generate meta.json

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")                                 # Generate tree.json
```

### Generating meta for a Single Component

```bash
cd engine/components/astronverse-browser
uv run meta.py
```

### Generating meta for All Components and Merging into Global Configuration

```bash
cd engine
uv run scripts/meta_build.py
```

Output:
- `resources/meta/meta.json` — Complete atomic capability configuration
- `resources/meta/tree.json` — Complete capability tree configuration

---

### Adding a New Atomic Capability Component

The following example demonstrates the complete workflow for adding a new "text encryption" component `astronverse-myencrypt`.

**Step 1: Create the component directory structure**

```
engine/components/astronverse-myencrypt/
├── src/
│   └── astronverse/
│       └── myencrypt/
│           ├── __init__.py       # Enum definitions
│           └── myencrypt.py      # Atomic capability implementation
├── config.yaml                   # UI configuration
├── meta.py                       # meta generation entry point
└── pyproject.toml                # Dependency declaration
```

**Step 2: Declare dependencies in `pyproject.toml`**

```toml
[project]
name = "astronverse-myencrypt"
version = "1.0.0"
description = "my encrypt component."
requires-python = ">=3.13"

dependencies = [
    "astronverse-actionlib",
]

[tool.uv.sources]
astronverse-actionlib = {path = "../../shared/astronverse-actionlib", editable = true}

[tool.hatch.build.targets.wheel]
packages = ["src/astronverse"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Define enums in `src/astronverse/myencrypt/__init__.py`**

```python
from enum import Enum

class CaseType(Enum):
    LOWER = "lower"
    UPPER = "upper"
```

**Step 4: Implement the atomic capability in `src/astronverse/myencrypt/myencrypt.py`**

```python
import hashlib
from astronverse.actionlib.atomic import atomicMg
from astronverse.myencrypt import CaseType


class MyEncrypt:
    @atomicMg.atomic()
    def md5_encrypt(self, source_str: str, case_type: CaseType = CaseType.LOWER) -> str:
        result = hashlib.md5(source_str.encode()).hexdigest()
        return result.upper() if case_type == CaseType.UPPER else result
```

**Step 5: Configure `config.yaml`**

```yaml
atomic:
  MyEncrypt.md5_encrypt:
    title: MD5 Encrypt
    icon: md5-encrypt
    comment: MD5 encrypt @{source_str} and output @{encrypted_result}
    helpManual: ''
    path:
      - /atomicTree/os/encrypt
    inputList:
      - key: source_str
        title: String to Encrypt
        tip: Enter the text to encrypt
      - key: case_type
        title: Result Case
        tip: Choose the case format of the encrypted result
    outputList:
      - key: encrypted_result
        title: Encrypted Result

options:
  CaseType:
    - value: lower
      label: Lowercase
    - value: upper
      label: Uppercase
```

**Step 6: Write `meta.py`**

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg
from astronverse.myencrypt.myencrypt import MyEncrypt

if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(MyEncrypt, version="1.0.0")
    atomicMg.meta()

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")
```

**Step 7: Register the component in `engine/pyproject.toml`**

The new component must be declared in `engine/pyproject.toml` before `uv sync` can recognize and install it. Add one line in each of the two sections:

1. Add the package name to the `dependencies` list:

```toml
dependencies = [
    # ... existing entries ...
    "astronverse-encrypt",
    "astronverse-myencrypt",   # add this line
]
```

2. Add the local path entry (editable mode) under `[tool.uv.sources]`:

```toml
[tool.uv.sources]
# ... existing entries ...
astronverse-encrypt = {path = "./components/astronverse-encrypt", editable = true}
astronverse-myencrypt = {path = "./components/astronverse-myencrypt", editable = true}  # add this line
```

**Step 8: Sync dependencies and generate meta**

```bash
# Sync dependencies in the engine directory to activate the new component
cd engine
uv sync

# Generate meta for the new component
cd components/astronverse-myencrypt
uv run meta.py

# Or regenerate global meta for all components at once
cd engine/scripts
uv run meta_build.py
```

Once completed, `meta.json` and `tree.json` will be generated in the component directory, and `resources/meta/meta.json` and `resources/meta/tree.json` will also be updated.

---

## End-to-End Debugging

Refer to [engine/DEVELOP.md](../DEVELOP.md) for details.

### Debugging a Component Individually

You can run specific modules or tests within a component directly:

```bash
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

---

## Code Standards

- The `path` field of atomic capabilities must follow the `/path1/path2/...` format; a validation error will be thrown at build time otherwise.
- Generated files such as `meta.json` and `tree.json` should not be edited manually — regenerate them via `meta.py`.
- Use `pylint` for code linting.

---

If you have any questions, please contact the project maintainers.
