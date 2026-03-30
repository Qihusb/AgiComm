@echo off
REM AgiComm 完整部署构建脚本 (Windows)

setlocal enabledelayedexpansion

echo ======================================
echo 🔨 AgiComm 一键部署构建 (Windows)
echo ======================================
echo.

REM 检查依赖
echo ✓ 检查依赖环境...
python --version >nul 2>&1 || (
  echo ❌ Python 未安装，请先安装 Python 3.8+
  pause
  exit /b 1
)

node --version >nul 2>&1 || (
  echo ❌ Node.js 未安装，请先安装 Node.js 16+
  pause
  exit /b 1
)

echo   • Python: %ProgramFiles%\Python
echo   • Node.js: %ProgramFiles%\nodejs
echo.

REM 安装后端依赖
echo 📦 安装后端依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
  echo ❌ 后端依赖安装失败
  pause
  exit /b 1
)
echo   ✓ 后端依赖安装完成
echo.

REM 构建前端
echo 🎨 构建前端...
cd frontend
call npm install -q
call npm run build
if errorlevel 1 (
  echo ❌ 前端构建失败
  pause
  exit /b 1
)
cd ..
echo   ✓ 前端构建完成 (dist/)
echo.

REM 汇总输出
echo ✅ 构建完成！
echo.
echo 📍 部署物料：
echo   • 前端: frontend\dist\ （已含入后端服务）
echo   • 后端: src\modules\api.py
echo   • 依赖: requirements.txt
echo.
echo 🚀 启动命令：
echo   开发环境: python -m src.modules.api
echo   生产环境: gunicorn -w 4 -b 0.0.0.0:8001 src.modules.api:app
echo.
pause
