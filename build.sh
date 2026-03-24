#!/usr/bin/env bash
set -euo pipefail

# Save script directory path IMMEDIATELY
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================
# 1. Argument Parsing
# ============================================

PYTHON_EXE=""
SEVENZ_EXE=""
SKIP_ENGINE=0
SKIP_FRONTEND=0

show_help() {
    echo ""
    echo "Usage: build.sh [options]"
    echo ""
    echo "Options:"
    echo "  --python-exe, -p <path>   Specify Python executable path"
    echo "  --sevenz-exe, -s <path>   Specify 7z executable path"
    echo "  --skip-engine              Skip engine (Python) build"
    echo "  --skip-frontend            Skip frontend build"
    echo "  --help, -h                 Display this help message"
    echo ""
    echo "Examples:"
    echo "  build.sh --python-exe /usr/local/bin/python3"
    echo "  build.sh -p /usr/local/bin/python3 -s /usr/local/bin/7zz"
    echo "  build.sh --skip-frontend"
    echo "  build.sh --skip-engine"
    echo ""
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python-exe|-p)
            PYTHON_EXE="$2"; shift 2 ;;
        --sevenz-exe|-s)
            SEVENZ_EXE="$2"; shift 2 ;;
        --skip-engine)
            SKIP_ENGINE=1; shift ;;
        --skip-frontend)
            SKIP_FRONTEND=1; shift ;;
        --help|-h)
            show_help ;;
        *)
            echo "Unknown parameter: $1"
            show_help ;;
    esac
done

# ============================================
# 2. Configuration
# ============================================

# Detect OS for default paths
if [[ "$(uname)" == "Darwin" ]]; then
    : "${PYTHON_EXE:=/usr/local/bin/python3}"
    : "${SEVENZ_EXE:=/usr/local/bin/7zz}"
else
    : "${PYTHON_EXE:=/usr/bin/python3}"
    : "${SEVENZ_EXE:=/usr/bin/7zz}"
fi

ENGINE_DIR="engine"
BUILD_DIR="build"
PYTHON_CORE_DIR="${BUILD_DIR}/python_core"
DIST_DIR="${BUILD_DIR}/dist"
ARCHIVE_DIST_DIR="resources"

# ============================================
# 3. Environment Check
# ============================================

if [[ "$SKIP_ENGINE" == "1" && "$SKIP_FRONTEND" == "1" ]]; then
    echo "Error: Cannot skip both engine and frontend builds"
    exit 1
fi

if [[ "$SKIP_ENGINE" != "1" ]]; then
    if [[ ! -x "$PYTHON_EXE" ]]; then
        echo "Local Python environment not found: $PYTHON_EXE"
        echo "Please set PYTHON_EXE by one of the following methods:"
        echo "  1. Use parameter: build.sh --python-exe <path>"
        echo "  2. Set environment variable: export PYTHON_EXE=/path/to/python3"
        echo "  3. Modify default value in build.sh"
        exit 1
    fi

    if [[ ! -x "$SEVENZ_EXE" ]]; then
        echo "7z not found: $SEVENZ_EXE"
        echo "Please set SEVENZ_EXE by one of the following methods:"
        echo "  1. Use parameter: build.sh --sevenz-exe <path>"
        echo "  2. Set environment variable: export SEVENZ_EXE=/path/to/7zz"
        echo "  3. Modify default value in build.sh"
        exit 1
    fi

    if ! uv --version > /dev/null 2>&1; then
        echo "uv not found, please install uv first, https://docs.astral.sh/uv/, and ensure uv command is in environment variables"
        exit 1
    fi
fi

# ============================================
# 4. Engine Build
# ============================================

if [[ "$SKIP_ENGINE" == "1" ]]; then
    echo ""
    echo "============================================"
    echo "Engine Build Skipped"
    echo "============================================"
else
    echo ""
    echo "============================================"
    echo "Starting Engine Build"
    echo "============================================"

    # ============================================
    # 4.1. Environment Setup
    # ============================================

    echo "Cleaning dist directory..."
    if [[ -d "$DIST_DIR" ]]; then
        rm -rf "$DIST_DIR" || { echo "Failed to clean dist directory"; exit 1; }
    fi

    echo "Cleaning requirements.txt..."
    if [[ -f "${ENGINE_DIR}/requirements.txt" ]]; then
        rm -f "${ENGINE_DIR}/requirements.txt" || { echo "Failed to delete requirements.txt"; exit 1; }
    fi

    if [[ -f "${ENGINE_DIR}/pyproject.toml.backup" ]]; then
        mv -f "${ENGINE_DIR}/pyproject.toml.backup" "${ENGINE_DIR}/pyproject.toml"
    fi

    echo "Creating build directory structure..."
    mkdir -p "$BUILD_DIR" "$DIST_DIR" "$PYTHON_CORE_DIR" "$ARCHIVE_DIST_DIR"

    # On Windows, python.exe sits directly in the Python root.
    # On Mac/Linux, python3 sits in <root>/bin/, so we need the grandparent.
    _PYTHON_PARENT="$(dirname "$PYTHON_EXE")"
    if [[ "$(basename "$_PYTHON_PARENT")" == "bin" ]]; then
        PYTHON_SOURCE_DIR="$(dirname "$_PYTHON_PARENT")"
    else
        PYTHON_SOURCE_DIR="$_PYTHON_PARENT"
    fi
    if [[ ! -f "${PYTHON_CORE_DIR}/bin/python3" && ! -f "${PYTHON_CORE_DIR}/bin/python" && ! -f "${PYTHON_CORE_DIR}/python3" && ! -f "${PYTHON_CORE_DIR}/python" ]]; then
        echo "Copying Python environment..."
        if [[ -d "$PYTHON_SOURCE_DIR" ]]; then
            cp -a "${PYTHON_SOURCE_DIR}/." "${PYTHON_CORE_DIR}/" || { echo "Python directory copy failed"; exit 1; }
            echo "Python environment copied successfully"
        else
            echo "${PYTHON_SOURCE_DIR} directory not found"
            exit 1
        fi
    else
        echo "Python environment already exists, skipping copy..."
    fi

    # ============================================
    # 4.2. Build Packages
    # ============================================

    echo "Backing up original and adding workspace"
    cp "${ENGINE_DIR}/pyproject.toml" "${ENGINE_DIR}/pyproject.toml.backup"

    echo "Building workspace members list..."
    WORKSPACE_MEMBERS=""

    # Check shared/* directories
    for d in "${ENGINE_DIR}/shared"/*/; do
        [[ -f "${d}pyproject.toml" ]] || continue
        name="$(basename "$d")"
        WORKSPACE_MEMBERS="${WORKSPACE_MEMBERS} \"shared/${name}\","
    done

    # Check servers/* directories
    for d in "${ENGINE_DIR}/servers"/*/; do
        [[ -f "${d}pyproject.toml" ]] || continue
        name="$(basename "$d")"
        WORKSPACE_MEMBERS="${WORKSPACE_MEMBERS} \"servers/${name}\","
    done

    # Check components/* directories
    for d in "${ENGINE_DIR}/components"/*/; do
        [[ -f "${d}pyproject.toml" ]] || continue
        name="$(basename "$d")"
        if [[ "$name" != "astronverse-database" ]]; then
            WORKSPACE_MEMBERS="${WORKSPACE_MEMBERS} \"components/${name}\","
        fi
    done

    # Remove trailing comma
    if [[ -n "$WORKSPACE_MEMBERS" ]]; then
        WORKSPACE_MEMBERS="${WORKSPACE_MEMBERS%,}"
    else
        echo "Warning: No valid workspace members found"
        WORKSPACE_MEMBERS='""'
    fi

    printf '\n[tool.uv.workspace]\nmembers = [%s]\n' "$WORKSPACE_MEMBERS" >> "${ENGINE_DIR}/pyproject.toml"

    echo "Starting batch build of all packages..."
    if ! uv build --project "$ENGINE_DIR" --all-packages --wheel --out-dir "$DIST_DIR"; then
        mv "${ENGINE_DIR}/pyproject.toml.backup" "${ENGINE_DIR}/pyproject.toml"
        exit 1
    fi
    mv "${ENGINE_DIR}/pyproject.toml.backup" "${ENGINE_DIR}/pyproject.toml"
    echo "All packages built successfully"

    # ============================================
    # 4.3. Install Packages
    # ============================================

    echo "Upgrading pip..."
    _PY_FOR_PIP=""
    for _p in "${PYTHON_CORE_DIR}/bin/python3" "${PYTHON_CORE_DIR}/bin/python" \
               "${PYTHON_CORE_DIR}/python3" "${PYTHON_CORE_DIR}/python"; do
        [[ -x "$_p" ]] && { _PY_FOR_PIP="$_p"; break; }
    done
    [[ -n "$_PY_FOR_PIP" ]] && "$_PY_FOR_PIP" -m pip install --upgrade pip 2>/dev/null || true

    echo "Generating requirements.txt from built packages..."
    # Extract package names from wheel filenames
    {
        echo "# Generated requirements from built packages"
        for whl in "${DIST_DIR}"/*.whl; do
            [[ -f "$whl" ]] || continue
            base="$(basename "$whl" .whl)"
            # Wheel format: name-version-pythontag-abitag-platformtag
            # Remove everything from the first -digit onwards
            name="${base%%-[[:digit:]]*}"
            # Replace underscores with hyphens
            echo "${name//_/-}"
        done
    } > "${ENGINE_DIR}/requirements.txt"

    echo "Installing packages from requirements.txt..."
    # Support both flat layout (Windows-style) and bin/ layout (Mac/Linux-style)
    if [[ -x "${PYTHON_CORE_DIR}/bin/python3" ]]; then
        PYTHON_BIN="${PYTHON_CORE_DIR}/bin/python3"
    elif [[ -x "${PYTHON_CORE_DIR}/bin/python" ]]; then
        PYTHON_BIN="${PYTHON_CORE_DIR}/bin/python"
    elif [[ -x "${PYTHON_CORE_DIR}/python3" ]]; then
        PYTHON_BIN="${PYTHON_CORE_DIR}/python3"
    else
        PYTHON_BIN="${PYTHON_CORE_DIR}/python"
    fi
    if ! uv pip install --link-mode=copy --python "$PYTHON_BIN" \
            --find-links="$DIST_DIR" -r "${ENGINE_DIR}/requirements.txt" \
            --upgrade --force-reinstall \
            -i https://pypi.tuna.tsinghua.edu.cn/simple; then
        echo "Package installation failed"
        exit 1
    fi
    echo "Batch installation successful"

    # ============================================
    # 4.4. Package and Release
    # ============================================

    echo "Compressing python_core directory..."
    ARCHIVE_PATH="${SCRIPT_DIR}/${ARCHIVE_DIST_DIR}/python_core.7z"
    (cd "$PYTHON_CORE_DIR" && "$SEVENZ_EXE" a -t7z "$ARCHIVE_PATH" "*" > /dev/null) \
        || { echo "python_core directory compression failed"; exit 1; }
    echo "Python_core directory compressed successfully, file saved to: ${ARCHIVE_PATH}"

    # Generate SHA-256 checksum file
    HASH_FILE="${SCRIPT_DIR}/${ARCHIVE_DIST_DIR}/python_core.7z.sha256.txt"
    if command -v shasum > /dev/null 2>&1; then
        shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}' > "$HASH_FILE"
    elif command -v sha256sum > /dev/null 2>&1; then
        sha256sum "$ARCHIVE_PATH" | awk '{print $1}' > "$HASH_FILE"
    else
        echo "SHA-256 generation failed: no shasum or sha256sum found"
        exit 1
    fi
    echo "Hash file generated: ${HASH_FILE}"

    echo ""
    echo "============================================"
    echo "Engine Build Complete!"
    echo "============================================"
fi

# ============================================
# 5. Frontend Build
# ============================================

if [[ "$SKIP_FRONTEND" == "1" ]]; then
    echo ""
    echo "============================================"
    echo "Frontend Build Skipped"
    echo "============================================"
else
    echo ""
    echo "============================================"
    echo "Starting Frontend Build"
    echo "============================================"

    echo "Checking pnpm installation..."
    if ! pnpm --version > /dev/null 2>&1; then
        echo ""
        echo "ERROR: pnpm not found, please install pnpm first: npm install -g pnpm"
        exit 1
    fi
    echo "pnpm check passed"

    echo "Navigating to frontend directory: ${SCRIPT_DIR}/frontend"
    cd "${SCRIPT_DIR}/frontend" || { echo "Frontend directory not found: ${SCRIPT_DIR}/frontend"; exit 1; }
    echo "Successfully entered frontend directory"
    echo "Current directory: $(pwd)"

    echo "Checking for package.json..."
    if [[ ! -f "package.json" ]]; then
        echo "ERROR: package.json not found in frontend directory"
        cd "$SCRIPT_DIR"
        exit 1
    fi

    echo "Installing dependencies..."
    pnpm install || { echo "pnpm install failed"; cd "$SCRIPT_DIR"; exit 1; }

    echo "Building desktop application..."
    if [[ "$(uname)" == "Darwin" ]]; then
        BUILD_CMD="build:mac"
    else
        BUILD_CMD="build:linux"
    fi
    echo "Detected platform: $(uname), using pnpm ${BUILD_CMD}"
    pnpm --filter astron-rpa "$BUILD_CMD" || { echo "Desktop application build failed"; cd "$SCRIPT_DIR"; exit 1; }

    echo "Frontend build completed successfully"

    cd "$SCRIPT_DIR"
fi

echo ""
echo "============================================"
echo "Full Build Complete!"
echo "============================================"
echo ""
echo "Installation package location:"
echo "  Frontend installer: frontend/packages/electron-app/dist/"
