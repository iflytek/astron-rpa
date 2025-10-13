@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM 1. Configuration
REM ============================================

if "%PYTHON_EXE%"=="" set PYTHON_EXE=C:\Program Files\Python313\python.exe
if "%SEVENZ_EXE%"=="" set SEVENZ_EXE=C:\Program Files\7-Zip\7z.exe
set BUILD_DIR=build
set PYTHON_CORE_DIR=%BUILD_DIR%\python_core
set DIST_DIR=%BUILD_DIR%\dist
set ARCHIVE_DIST_DIR=../resources/

REM ============================================
REM 2. Argument Parsing
REM ============================================


REM ============================================
REM 3. Environment Check
REM ============================================

if not exist "%PYTHON_EXE%" (
    echo Local Python environment not found: %PYTHON_EXE%, please set PYTHON_EXE in build.bat
    exit /b 1
)

uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found, please install uv first, https://docs.astral.sh/uv/, and ensure uv command is in environment variables
    exit /b 1
)

if not exist "%SEVENZ_EXE%" (
    echo 7z.exe not found: %SEVENZ_EXE%, please set SEVENZ_EXE in build.bat
    exit /b 1
)


REM ============================================
REM 4. Environment Setup
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
if exist requirements.txt (
    del /q requirements.txt
    if errorlevel 1 (
        echo Failed to delete requirements.txt
        exit /b 1
    )
)

if exist pyproject.toml.backup (
    move /y pyproject.toml.backup pyproject.toml >nul
)

echo Creating build directory structure...
if not exist %BUILD_DIR% mkdir %BUILD_DIR%
if not exist %DIST_DIR% mkdir %DIST_DIR%
if not exist %PYTHON_CORE_DIR% mkdir %PYTHON_CORE_DIR%
if not exist %ARCHIVE_DIST_DIR% mkdir %ARCHIVE_DIST_DIR%
for %%i in ("%PYTHON_EXE%") do set PYTHON_SOURCE_DIR=%%~di%%~pi
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
REM 5. Build Packages
REM ============================================

echo Backing up original and adding workspace
copy pyproject.toml pyproject.toml.backup >nul
echo. >> pyproject.toml
echo [tool.uv.workspace] >> pyproject.toml
echo members = ["shared/*", "servers/*", "components/*"] >> pyproject.toml

echo Starting batch build of all packages...
uv build --all-packages --wheel --out-dir "%DIST_DIR%"
if errorlevel 1 (
    move pyproject.toml.backup pyproject.toml >nul
    exit /b 1
)
move pyproject.toml.backup pyproject.toml >nul
echo ✓ All packages built successfully

REM ============================================
REM 6. Install Packages
REM ============================================

echo Upgrading pip...
%PYTHON_CORE_DIR%\python.exe -m pip install --upgrade pip 2>nul

echo Generating requirements.txt from built packages...

REM Generate requirements.txt from wheel files using PowerShell
powershell -Command "$files = Get-ChildItem '%DIST_DIR%\*.whl' | ForEach-Object { $name = $_.BaseName -replace '_','-'; $name -replace '-\d+\.\d+\.\d+-py3-none-any$','' }; Set-Content -Path 'requirements.txt' -Value '# Generated requirements from built packages'; Add-Content -Path 'requirements.txt' -Value $files"

echo Installing packages from requirements.txt...
uv pip install --link-mode=copy --python "%PYTHON_CORE_DIR%\python.exe" --find-links="%DIST_DIR%" -r "requirements.txt"
if errorlevel 1 (
    echo Package installation failed
    exit /b 1
)
echo ✓ Batch installation successful

REM ============================================
REM 7. Package and Release
REM ============================================

echo Compressing python_core directory...
cd /d "%PYTHON_CORE_DIR%"
"%SEVENZ_EXE%" a -t7z "%~dp0%ARCHIVE_DIST_DIR%\python_core.7z" "*" >nul
cd /d "%~dp0"
if errorlevel 1 (
    echo python_core directory compression failed
    exit /b 1
)
echo ✓ python_core directory compressed successfully, file saved to: %ARCHIVE_DIST_DIR%\python_core.7z

echo.
echo ============================================
echo Engine Build Script
echo Complete!
echo ============================================
