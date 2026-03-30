#!/bin/bash
# AgiComm 服务启动脚本 (Linux/macOS)

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 变量
MODE=${1:-"production"}
PORT=${API_PORT:-8001}
WORKERS=${GUNICORN_WORKERS:-4}
TIMEOUT=${REQUEST_TIMEOUT:-120}

# 打印函数
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查环境
check_env() {
    print_header "检查环境"
    
    # 检查 Python
    if ! command -v python &> /dev/null; then
        print_error "Python 未安装"
    fi
    print_success "Python 已安装: $(python --version)"
    
    # 检查 pip
    if ! command -v pip &> /dev/null; then
        print_error "pip 未安装"
    fi
    print_success "pip 已安装"
    
    # 检查配置文件
    if [ ! -f ".env.production" ] && [ "$MODE" = "production" ]; then
        print_warning ".env.production 不存在"
        if [ -f ".env.production.example" ]; then
            print_info "使用 .env.production.example 作为模板"
            cp .env.production.example .env.production
            print_warning "请编辑 .env.production 填入真实的 API 密钥"
            exit 1
        fi
    fi
    
    print_success "环境检查通过"
}

# 检查依赖
check_dependencies() {
    print_header "检查依赖"
    
    # 检查必要的 Python 包
    python -c "import fastapi" 2>/dev/null && print_success "fastapi" || print_error "fastapi 未安装，运行: pip install -r requirements.txt"
    python -c "import gunicorn" 2>/dev/null && print_success "gunicorn" || print_error "gunicorn 未安装，运行: pip install -r requirements.txt"
    
    print_success "依赖检查通过"
}

# 检查前端
check_frontend() {
    print_header "检查前端"
    
    if [ ! -d "frontend/dist" ]; then
        print_warning "前端未构建"
        print_info "构建前端..."
        cd frontend
        npm install
        npm run build
        cd ..
        print_success "前端构建完成"
    else
        print_success "前端已构建"
    fi
}

# 启动开发服务器
start_dev() {
    print_header "启动开发服务器"
    
    print_info "监听端口: $PORT"
    print_info "API 文档: http://localhost:$PORT/docs"
    print_info "前端: http://localhost:$PORT"
    print_info "按 Ctrl+C 停止服务"
    
    python -m src.modules.api
}

# 启动生产服务器
start_production() {
    print_header "启动生产服务器"
    
    # 检查端口是否被占用
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        print_error "端口 $PORT 已被占用"
    fi
    
    print_info "工作进程数: $WORKERS (建议值: CPU核数*2+1)"
    print_info "请求超时: ${TIMEOUT}s"
    print_info "监听端口: $PORT"
    print_info ""
    
    # 启动 Gunicorn
    gunicorn \
        -w $WORKERS \
        -b 0.0.0.0:$PORT \
        --timeout $TIMEOUT \
        --access-logfile gunicorn.log \
        --error-logfile gunicorn.log \
        --log-level info \
        src.modules.api:app
}

# 显示使用说明
show_usage() {
    echo "AgiComm 服务启动脚本"
    echo ""
    echo "用法: $0 [mode] [options]"
    echo ""
    echo "Mode:"
    echo "  dev          - 启动开发服务器 (python -m)"
    echo "  production   - 启动生产服务器 (gunicorn) [默认]"
    echo "  check        - 仅运行环境检查"
    echo "  help         - 显示此帮助信息"
    echo ""
    echo "Options:"
    echo "  API_PORT=8001              - 自定义端口 (默认: 8001)"
    echo "  GUNICORN_WORKERS=8         - 自定义工作进程数 (默认: 4)"
    echo "  REQUEST_TIMEOUT=300        - 自定义超时时间 (默认: 120s)"
    echo ""
    echo "示例:"
    echo "  $0 dev                     - 开发模式"
    echo "  $0 production              - 生产模式（4个工作进程）"
    echo "  API_PORT=9000 $0 production - 使用 9000 端口的生产模式"
    echo ""
}

# 主程序
main() {
    case "$MODE" in
        "dev")
            check_env
            check_frontend
            start_dev
            ;;
        "production")
            check_env
            check_dependencies
            check_frontend
            start_production
            ;;
        "check")
            check_env
            check_dependencies
            check_frontend
            print_success "所有检查通过"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "未知的模式: $MODE"
            show_usage
            exit 1
            ;;
    esac
}

# 运行主程序
main
