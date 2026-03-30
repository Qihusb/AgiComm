@echo off
REM AgiComm 服务启动脚本 (Windows)

setlocal enabledelayedexpansion

REM 颜色代码 (Windows 10+)
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM 默认变量
set MODE=%1
if "%MODE%"=="" set MODE=production

set API_PORT=%API_PORT%
if "%API_PORT%"=="" set API_PORT=8001

set GUNICORN_WORKERS=%GUNICORN_WORKERS%
if "%GUNICORN_WORKERS%"=="" set GUNICORN_WORKERS=4

set REQUEST_TIMEOUT=%REQUEST_TIMEOUT%
if "%REQUEST_TIMEOUT%"=="" set REQUEST_TIMEOUT=120

REM 打印函数
:print_header
echo.
echo ============================================================
echo %~1
echo ============================================================
echo.
exit /b

:print_success
echo [+] %~1
exit /b

:print_error
echo [-] %~1
pause
exit /b 1

:print_warning
echo [!] %~1
exit /b

:print_info
echo [*] %~1
exit /b

REM 检查环境
:check_env
call :print_header "检查环境"

python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python 未安装"
    exit /b 1
)
call :print_success "Python 已安装"

pip --version >nul 2>&1
if errorlevel 1 (
    call :print_error "pip 未安装"
    exit /b 1
)
call :print_success "pip 已安装"

if "%MODE%"=="production" (
    if not exist ".env.production" (
        if exist ".env.production.example" (
            call :print_warning ".env.production 不存在，使用示例文件"
            copy .env.production.example .env.production >nul
            call :print_warning "请编辑 .env.production 填入真实的 API 密钥"
            exit /b 1
        )
    )
)

call :print_success "环境检查通过"
exit /b

REM 检查依赖
:check_dependencies
call :print_header "检查依赖"

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    call :print_error "fastapi 未安装，运行: pip install -r requirements.txt"
    exit /b 1
)
call :print_success "fastapi 已安装"

python -c "import gunicorn" >nul 2>&1
if errorlevel 1 (
    call :print_error "gunicorn 未安装，运行: pip install -r requirements.txt"
    exit /b 1
)
call :print_success "gunicorn 已安装"

call :print_success "依赖检查通过"
exit /b

REM 检查前端
:check_frontend
call :print_header "检查前端"

if not exist "frontend\dist" (
    call :print_warning "前端未构建"
    call :print_info "构建前端..."
    cd frontend
    call npm install
    if errorlevel 1 (
        call :print_error "npm install 失败"
        exit /b 1
    )
    call npm run build
    if errorlevel 1 (
        call :print_error "前端构建失败"
        exit /b 1
    )
    cd ..
    call :print_success "前端构建完成"
) else (
    call :print_success "前端已构建"
)
exit /b

REM 启动开发服务器
:start_dev
call :print_header "启动开发服务器"

call :print_info "监听端口: %API_PORT%"
call :print_info "API 文档: http://localhost:%API_PORT%/docs"
call :print_info "前端: http://localhost:%API_PORT%"
call :print_info "按 Ctrl+C 停止服务"
echo.

python -m src.modules.api
exit /b

REM 启动生产服务器
:start_production
call :print_header "启动生产服务器"

call :print_info "工作进程数: %GUNICORN_WORKERS% (建议值: CPU核数*2+1)"
call :print_info "请求超时: %REQUEST_TIMEOUT%s"
call :print_info "监听端口: %API_PORT%"
call :print_info "访问: http://localhost:%API_PORT%"
echo.

REM 检查文件是否存在
if not exist src\modules\api.py (
    call :print_error "src\modules\api.py 不存在"
    exit /b 1
)

gunicorn ^
    -w %GUNICORN_WORKERS% ^
    -b 0.0.0.0:%API_PORT% ^
    --timeout %REQUEST_TIMEOUT% ^
    --access-logfile gunicorn.log ^
    --error-logfile gunicorn.log ^
    --log-level info ^
    src.modules.api:app
exit /b

REM 显示使用说明
:show_usage
echo AgiComm 服务启动脚本
echo.
echo 用法: %0 [mode]
echo.
echo Mode:
echo   dev          - 启动开发服务器 (python -m)
echo   production   - 启动生产服务器 (gunicorn) [默认]
echo   check        - 仅运行环境检查
echo   help         - 显示此帮助信息
echo.
echo 示例:
echo   %0 dev                   - 开发模式
echo   %0 production            - 生产模式
echo   set API_PORT=9000 ^& %0  - 使用 9000 端口
echo.
exit /b

REM 主程序
:main
if "%MODE%"=="dev" (
    call :check_env
    if errorlevel 1 exit /b 1
    call :check_frontend
    if errorlevel 1 exit /b 1
    call :start_dev
) else if "%MODE%"=="production" (
    call :check_env
    if errorlevel 1 exit /b 1
    call :check_dependencies
    if errorlevel 1 exit /b 1
    call :check_frontend
    if errorlevel 1 exit /b 1
    call :start_production
) else if "%MODE%"=="check" (
    call :check_env
    if errorlevel 1 exit /b 1
    call :check_dependencies
    if errorlevel 1 exit /b 1
    call :check_frontend
    if errorlevel 1 exit /b 1
    call :print_success "所有检查通过"
) else if "%MODE%"=="help" (
    call :show_usage
) else (
    call :print_error "未知的模式: %MODE%"
    call :show_usage
    exit /b 1
)

endlocal
exit /b
