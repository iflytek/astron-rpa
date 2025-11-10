@echo off
chcp 65001 >nul

REM Save script directory path IMMEDIATELY
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

setlocal enabledelayedexpansion

REM ============================================
REM 1. Argument Parsing
REM ============================================

:parse_args
if "%~1"=="" goto end_parse_args
if /i "%~1"=="--python-exe" (
    set PYTHON_EXE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="-p" (
    set PYTHON_EXE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--sevenz-exe" (
    set SEVENZ_EXE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="-s" (
    set SEVENZ_EXE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--skip-engine" (
    set SKIP_ENGINE=1
    shift
    goto parse_args
)
if /i "%~1"=="--skip-frontend" (
    set SKIP_FRONTEND=1
    shift
    goto parse_args
)
if /i "%~1"=="--help" goto show_help
if /i "%~1"=="-h" goto show_help
echo Unknown parameter: %~1
goto show_help

:show_help
echo.
echo Usage: build.bat [options]
echo.
echo Options:
echo   --python-exe, -p ^<path^>   Specify Python executable path
echo   --sevenz-exe, -s ^<path^>   Specify 7-Zip executable path
echo   --skip-engine              Skip engine (Python) build
echo   --skip-frontend            Skip frontend build
echo   --help, -h                 Display this help message
echo.
echo Examples:
echo   build.bat --python-exe "C:\Python313\python.exe"
echo   build.bat -p "C:\Python313\python.exe" -s "C:\7-Zip\7z.exe"
echo   build.bat --skip-frontend
echo   build.bat --skip-engine
echo.
exit /b 1

:end_parse_args

REM ============================================
REM 2. Configuration
REM ============================================

if "%PYTHON_EXE%"=="" set PYTHON_EXE=C:\Program Files\Python313\python.exe
if "%SEVENZ_EXE%"=="" set SEVENZ_EXE=C:\Program Files\7-Zip\7z.exe
set ENGINE_DIR=engine
set BUILD_DIR=build
set PYTHON_CORE_DIR=%BUILD_DIR%\python_core
set DIST_DIR=%BUILD_DIR%\dist
set ARCHIVE_DIST_DIR=resources

REM ============================================
REM 3. Environment Check
REM ============================================

REM Check if both engine and frontend are skipped
if "%SKIP_ENGINE%"=="1" if "%SKIP_FRONTEND%"=="1" (
    echo Error: Cannot skip both engine and frontend builds
    exit /b 1
)

REM Skip engine environment checks if engine build is disabled
if "%SKIP_ENGINE%"=="1" goto skip_engine_checks

if not exist "%PYTHON_EXE%" (
    echo Local Python environment not found: %PYTHON_EXE%
    echo Please set PYTHON_EXE by one of the following methods:
    echo   1. Use parameter: build.bat --python-exe "path"
    echo   2. Set environment variable: $env:PYTHON_EXE = "C:\Program Files\Python313\python.exe"
    echo   3. Modify default value in build.bat
    exit /b 1
)

if not exist "%SEVENZ_EXE%" (
    echo 7z.exe not found: %SEVENZ_EXE%
    echo Please set SEVENZ_EXE by one of the following methods:
    echo   1. Use parameter: build.bat --sevenz-exe "path"
    echo   2. Set environment variable: $env:SEVENZ_EXE = "C:\Program Files\7-Zip\7z.exe"
    echo   3. Modify default value in build.bat
    exit /b 1
)


uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found, please install uv first, https://docs.astral.sh/uv/, and ensure uv command is in environment variables
    exit /b 1
)

:skip_engine_checks

REM ============================================
REM 4. Engine Build
REM ============================================

if "%SKIP_ENGINE%"=="1" (
    echo.
    echo ============================================
    echo Engine Build Skipped
    echo ============================================
    goto skip_engine_build
)

echo.
echo ============================================
echo Starting Engine Build
echo ============================================

REM ============================================
REM 4.1. Environment Setup
REM ============================================

echo Cleaning dist directory...
if exist "%DIST_DIR%" (
    rmdir /s /q "%DIST_DIR%"
    if errorlevel 1 (
        echo Failed to clean dist directory
        exit /b 1
    )
)

echo Cleaning requirements.txt...
if exist %ENGINE_DIR%\requirements.txt (
    del /q %ENGINE_DIR%\requirements.txt
    if errorlevel 1 (
        echo Failed to delete requirements.txt
        exit /b 1
    )
)

if exist %ENGINE_DIR%\pyproject.toml.backup (
    move /y %ENGINE_DIR%\pyproject.toml.backup %ENGINE_DIR%\pyproject.toml >nul
)

echo Creating build directory structure...
if not exist %BUILD_DIR% mkdir %BUILD_DIR%
if not exist %DIST_DIR% mkdir %DIST_DIR%
if not exist %PYTHON_CORE_DIR% mkdir %PYTHON_CORE_DIR%
if not exist %ARCHIVE_DIST_DIR% mkdir %ARCHIVE_DIST_DIR%
for %%i in ("%PYTHON_EXE%") do set PYTHON_SOURCE_DIR=%%~dpi
if not exist "%PYTHON_CORE_DIR%\python.exe" (
    echo Copying Python environment...
    if exist "%PYTHON_SOURCE_DIR%" (
        xcopy /E /I /Y "%PYTHON_SOURCE_DIR%\*" "%PYTHON_CORE_DIR%\"
        if errorlevel 1 (
            echo Python directory copy failed
            exit /b 1
        )
        echo Python environment copied successfully
    ) else (
        echo %PYTHON_SOURCE_DIR% directory not found
        exit /b 1
    )
) else (
    echo Python environment already exists, skipping copy...
)

REM ============================================
REM 4.2. Build Packages
REM ============================================

echo Backing up original and adding workspace
copy %ENGINE_DIR%\pyproject.toml %ENGINE_DIR%\pyproject.toml.backup >nul
echo. >> %ENGINE_DIR%\pyproject.toml
echo [tool.uv.workspace] >> %ENGINE_DIR%\pyproject.toml
echo members = ["shared/*", "servers/*", "components/*"] >> %ENGINE_DIR%\pyproject.toml

echo Starting batch build of all packages...
uv build --project %ENGINE_DIR% --all-packages --wheel --out-dir "%DIST_DIR%"
if errorlevel 1 (
    move %ENGINE_DIR%\pyproject.toml.backup %ENGINE_DIR%\pyproject.toml >nul
    exit /b 1
)
move %ENGINE_DIR%\pyproject.toml.backup %ENGINE_DIR%\pyproject.toml >nul
echo All packages built successfully

REM ============================================
REM 4.3. Install Packages
REM ============================================

echo Upgrading pip...
%PYTHON_CORE_DIR%\python.exe -m pip install --upgrade pip 2>nul

echo Generating requirements.txt from built packages...

REM Generate requirements.txt from wheel files using PowerShell
powershell -Command "$files = Get-ChildItem '%DIST_DIR%\*.whl' | ForEach-Object { $name = $_.BaseName -replace '_','-'; $name -replace '-\d+\.\d+\.\d+-py3-none-any$','' }; Set-Content -Path '%ENGINE_DIR%\requirements.txt' -Value '# Generated requirements from built packages'; Add-Content -Path '%ENGINE_DIR%\requirements.txt' -Value $files"

echo Installing packages from requirements.txt...
uv pip install --link-mode=copy --python "%PYTHON_CORE_DIR%\python.exe" --find-links="%DIST_DIR%" -r "%ENGINE_DIR%\requirements.txt" --upgrade --force-reinstall
if errorlevel 1 (
    echo Package installation failed
    exit /b 1
)
echo Batch installation successful

REM ============================================
REM 4.4. Package and Release
REM ============================================

echo Compressing python_core directory...
cd /d "%PYTHON_CORE_DIR%"
"%SEVENZ_EXE%" a -t7z "%SCRIPT_DIR%\%ARCHIVE_DIST_DIR%\python_core.7z" "*" >nul
cd /d "%SCRIPT_DIR%"
if errorlevel 1 (
    echo python_core directory compression failed
    exit /b 1
)
echo Python_core directory compressed successfully, file saved to: %SCRIPT_DIR%\%ARCHIVE_DIST_DIR%\python_core.7z

echo.
echo ============================================
echo Engine Build Complete!
echo ============================================

:skip_engine_build

REM ============================================
REM 5. Frontend Build
REM ============================================

if "%SKIP_FRONTEND%"=="1" (
    echo.
    echo ============================================
    echo Frontend Build Skipped
    echo ============================================
    goto skip_frontend_build
)

echo.
echo ============================================
echo Starting Frontend Build
echo ============================================

echo Checking pnpm installation...
call pnpm --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ERROR: pnpm not found, please install pnpm first: npm install -g pnpm
    exit /b 1
)
echo pnpm check passed

echo Navigating to frontend directory: %SCRIPT_DIR%\frontend
cd /d "%SCRIPT_DIR%\frontend"
if errorlevel 1 (
    echo Frontend directory not found: %SCRIPT_DIR%\frontend
    exit /b 1
)
echo Successfully entered frontend directory
echo Current directory: %CD%

echo Checking for package.json...
if not exist "package.json" (
    echo ERROR: package.json not found in frontend directory
    cd /d "%SCRIPT_DIR%"
    exit /b 1
)

echo Installing dependencies...
call pnpm install
if !errorlevel! neq 0 (
    echo pnpm install failed
    cd /d "%SCRIPT_DIR%"
    exit /b 1
)

echo Configuring environment variables...
if not exist "packages\web-app\.env" (
    if exist "packages\web-app\.env.example" (
        copy packages\web-app\.env.example packages\web-app\.env
        echo Environment file created from .env.example
    ) else (
        echo Warning: .env.example not found, skipping environment configuration
    )
) else (
    echo Environment file already exists, skipping copy
)

echo Building web application...
call pnpm build:web
if !errorlevel! neq 0 (
    echo Web application build failed
    cd /d "%SCRIPT_DIR%"
    exit /b 1
)

echo Building desktop application...
call pnpm build:tauri-debug
if !errorlevel! neq 0 (
    echo Desktop application build failed
    cd /d "%SCRIPT_DIR%"
    exit /b 1
)

echo Frontend build completed successfully

REM Return to script directory
cd /d "%SCRIPT_DIR%"

:skip_frontend_build

echo.
echo ============================================
echo Full Build Complete!
echo ============================================
