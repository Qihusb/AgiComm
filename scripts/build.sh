#!/bin/bash
# AgiComm 完整部署构建脚本

set -e

echo "======================================"
echo "🔨 AgiComm 一键部署构建"
echo "======================================"
echo ""

# 1. 检查依赖
echo "✓ 检查依赖环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装，请先安装 Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16+"
    exit 1
fi

echo "  • Python: $(python3 --version)"
echo "  • Node.js: $(node --version)"
echo "  • npm: $(npm --version)"
echo ""

# 2. 安装后端依赖
echo "📦 安装后端依赖..."
pip install -r requirements.txt -q
echo "  ✓ 后端依赖安装完成"
echo ""

# 3. 构建前端
echo "🎨 构建前端..."
cd frontend
npm install -q
npm run build
cd ..
echo "  ✓ 前端构建完成（dist/）"
echo ""

# 4. 汇总输出
echo "✅ 构建完成！"
echo ""
echo "📍 部署物料："
echo "  • 前端: frontend/dist/ （已含入后端服务）"
echo "  • 后端: src/modules/api.py"
echo "  • 依赖: requirements.txt"
echo ""
echo "🚀 启动命令："
echo "  开发环境: python -m src.modules.api"
echo "  生产环境: gunicorn -w 4 -b 0.0.0.0:8001 src.modules.api:app"
echo ""
