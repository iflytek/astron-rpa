English | [简体中文](README.zh.md)
# Automatic Build of Meta Configuration Guide

This directory contains the `meta_build.py` script, which is executed from the `engine` uv project to build and merge component meta and tree configurations.

## Features

- Automatically execute `meta.py` in each component directory to generate/update the local `meta.json` and `tree.json`.
- Merge all component `meta.json` files with the base configuration `base_meta.json`, outputting to `resources/meta/meta.json`.
- Deep-merge all component `tree.json` files with the skeleton configuration `tree_frame.json`, outputting to `resources/meta/tree.json`.
- Merge all component `meta_type.json` type definitions.
- Leaf atomic nodes are always ordered before subtree nodes at the same level.

## Environment Setup

This script is run with [uv](https://docs.astral.sh/uv/) from the `engine` project root so it can reuse the engine project's dependencies.

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

No environment variables required.

## How to Use

1. Navigate to the `engine` directory:
  ```bash
  cd engine
  ```
2. Run the script:
  ```bash
  uv run scripts/meta_build.py
  ```

## Workflow

1. **Execute component meta.py**  
  The script automatically traverses the `components` directory, skips `astronverse-database`, and executes `meta.py` in each component's subdirectory to generate/update the corresponding `meta.json` and `tree.json`.

2. **Merge local meta.json files**  
  It aggregates all component `meta.json` files into a temporary file `temp_local_meta.json`.

3. **Merge local tree.json files**  
  It deep-merges all component `tree.json` files into a temporary file `temp_local_tree.json`. Nodes with the same key are merged recursively.

4. **Build final meta**  
  Merges local meta with `resources/meta/base_meta.json`, sorts by key, and outputs to `resources/meta/meta.json`.

5. **Build final tree**  
  Deep-merges local tree with `resources/meta/tree_frame.json` (skeleton config), also merging type definitions and common advanced parameters, outputting to `resources/meta/tree.json`.

## Output Files

| File | Description |
|------|-------------|
| `engine/scripts/temp_local_meta.json` | Temporary merged local component meta |
| `engine/scripts/temp_local_tree.json` | Temporary merged local component tree |
| `resources/meta/meta.json` | Final merged meta configuration |
| `resources/meta/tree.json` | Final merged tree configuration |

## Notes

- Directories to skip are configured in the `SKIPPED_COMPONENTS` list; `astronverse-database` is skipped by default.
- The merge logic prioritizes local component data; `tree_frame.json` provides the tree structure skeleton.

If you have any questions, please contact the project maintainer.
