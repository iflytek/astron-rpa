@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM 1. 配置
REM ============================================

set PYTHON_EXE=E:\Python313\python.exe
set SEVENZ_EXE=C:\Program Files\7-Zip\7z.exe
set BUILD_DIR=build
set PYTHON_CORE_DIR=%BUILD_DIR%\python_core
set DIST_DIR=%BUILD_DIR%\dist
set ARCHIVE_DIST_DIR=../frontend/packages/tauri-app/src-tauri/resources/

REM ============================================
REM 2. 参数解析
REM ============================================

set SHOW_HELP=false

:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="--help" (
    set SHOW_HELP=true
    shift
    goto parse_args
)
echo 未知参数: %~1
echo 使用 --help 查看帮助信息
exit /b 1
:end_parse

if "%SHOW_HELP%"=="true" (
    echo.
    echo ============================================
    echo Engine 构建脚本
    echo ============================================
    echo.
    echo 用法: build.bat [选项]
    echo.
    echo 选项:
    echo   --help    显示此帮助信息
    echo.
    echo ============================================
    echo.
    exit /b 0
)

REM ============================================
REM 3. 环境检查
REM ============================================

if not exist "%PYTHON_EXE%" (
    echo 未找到本地Python环境: %PYTHON_EXE%, 请设置build.bat的PYTHON_EXE
    exit /b 1
)

uv --version >nul 2>&1
if errorlevel 1 (
    echo 未找到uv，请先安装uv， https://docs.astral.sh/uv/, 并保证环境变量存在uv命令
    exit /b 1
)

if not exist "%SEVENZ_EXE%" (
    echo 未找到7z.exe: %SEVENZ_EXE%, 请设置build.bat的SEVENZ_EXE
    exit /b 1
)


REM ============================================
REM 4. 准备环境
REM ============================================

echo 创建构建目录结构...
if not exist %BUILD_DIR% mkdir %BUILD_DIR%
if not exist %DIST_DIR% mkdir %DIST_DIR%
if not exist %PYTHON_CORE_DIR% mkdir %PYTHON_CORE_DIR%
if not exist %ARCHIVE_DIST_DIR% mkdir %ARCHIVE_DIST_DIR%
for %%i in ("%PYTHON_EXE%") do set PYTHON_SOURCE_DIR=%%~di%%~pi
if not exist "%PYTHON_CORE_DIR%\python.exe" (
    echo 复制Python环境...
    if exist "%PYTHON_SOURCE_DIR%" (
        xcopy /E /I /Y "%PYTHON_SOURCE_DIR%\*" "%PYTHON_CORE_DIR%\"
        if errorlevel 1 (
            echo Python目录复制失败
            exit /b 1
        )
        echo Python环境复制成功
    ) else (
        echo 未找到%PYTHON_SOURCE_DIR%目录
        exit /b 1
    )
) else (
    echo Python环境已存在，跳过复制...
)

REM ============================================
REM 5. 构建包
REM ============================================

echo 备份原始并添加workspace
copy pyproject.toml pyproject.toml.backup >nul
echo. >> pyproject.toml
echo [tool.uv.workspace] >> pyproject.toml
echo members = ["shared/*", "servers/*", "components/*"] >> pyproject.toml

echo 开始批量构建所有包...
uv build --all-packages --wheel --out-dir "%DIST_DIR%"
if errorlevel 1 (
    move pyproject.toml.backup pyproject.toml >nul
    exit /b 1
)
move pyproject.toml.backup pyproject.toml >nul
echo ✓ 所有包批量构建成功

REM ============================================
REM 6. 安装包
REM ============================================

echo 升级pip...
%PYTHON_CORE_DIR%\python.exe -m pip install --upgrade pip 2>nul

echo 批量安装包...

REM 计算总包数量
set /a TOTAL_PACKAGES=0
for %%f in ("%DIST_DIR%\*.whl") do set /a TOTAL_PACKAGES+=1

REM 安装包并显示进度
set /a CURRENT_PACKAGE=0
for %%f in ("%DIST_DIR%\*.whl") do (
    set /a CURRENT_PACKAGE+=1
    echo [!CURRENT_PACKAGE!/%TOTAL_PACKAGES%] 安装 %%f...
    uv pip install --link-mode=copy --python "%PYTHON_CORE_DIR%\python.exe" --find-links="%DIST_DIR%" "%%f"
    if errorlevel 1 (
        echo [!CURRENT_PACKAGE!/%TOTAL_PACKAGES%] %%f 安装失败
        exit /b 1
    )
)
echo ✓ 批量安装成功

REM ============================================
REM 7. 打包发布
REM ============================================

echo 正在压缩python_core目录...
cd /d "%PYTHON_CORE_DIR%"
"%SEVENZ_EXE%" a -t7z "%~dp0%ARCHIVE_DIST_DIR%\python_core.7z" "*" >nul
cd /d "%~dp0"
if errorlevel 1 (
    echo python_core目录压缩失败
    exit /b 1
)
echo ✓ python_core目录压缩成功，文件保存至: %ARCHIVE_DIST_DIR%\python_core.7z

echo.
echo ============================================
echo Engine 构建脚本
echo 完成！
echo ============================================
