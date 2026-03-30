# 使用官方 Python 运行时作为基础镜像
FROM python:3.10-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 构建前端（需要 Node.js 环境）
FROM node:18-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 最终镜像
FROM python:3.10-slim
WORKDIR /app

# 复制依赖安装结果
COPY --from=build-stage /app .

# 复制前端构建结果
COPY --from=frontend /app/frontend/dist ./frontend/dist

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "--timeout", "120", "src.modules.api:app"]
