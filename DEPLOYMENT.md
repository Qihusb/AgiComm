# 🚀 AgiComm 服务器部署指南

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+ （前端构建）
- npm 或 yarn
- Git （可选，用于克隆代码）

### 一键部署

#### Linux / macOS

```bash
# 1. 进入项目目录
cd AgiComm

# 2. 运行构建脚本
bash scripts/build.sh

# 3. 配置环境变量
cp .env.production.example .env.production
# 编辑 .env.production，填入 API 密钥
nano .env.production

# 4. 启动生产服务
gunicorn -w 4 -b 0.0.0.0:8001 src.modules.api:app
```

#### Windows

```bash
# 1. 进入项目目录
cd AgiComm

# 2. 运行构建脚本
scripts\build.bat

# 3. 配置环境变量
copy .env.production.example .env.production
# 用编辑器打开 .env.production，填入 API 密钥

# 4. 启动生产服务
AgiComm>python -m src.modules.api
```

---

## 部署方案选择

### 方案 A: 直接启动（简单，适合小规模）

```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..

# 启动
AgiComm>python -m src.modules.api
```

**访问**: http://server-ip:8001

---

### 方案 B: Docker 部署（推荐，适合云平台）

```bash
# 构建镜像
docker build -t agicomm:latest .

# 运行容器
docker run -d \
  --name agicomm \
  -p 8001:8001 \
  -e ZHIPU_API_KEY=your_key_here \
  -e PRIMARY_PROVIDER=zhipu \
  agicomm:latest
```

**访问**: http://server-ip:8001

---

### 方案 C: Docker Compose（最完整，适合团队协作）

```bash
# 编辑 .env 填入 API 密钥
cp .env.production.example .env
nano .env

# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f agicomm

# 停止
docker-compose down
```

**访问**: http://server-ip:8001

---

### 方案 D: Nginx 反向代理 + Gunicorn（推荐用于生产）

#### 1. 启动后端服务

```bash
# 后台启动 Gunicorn
nohup gunicorn -w 4 -b 127.0.0.1:8001 src.modules.api:app > gunicorn.log 2>&1 &

# 或使用 systemd 管理（Linux）
sudo tee /etc/systemd/system/agicomm.service > /dev/null << EOF
[Unit]
Description=AgiComm API Server
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/AgiComm
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 src.modules.api:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable agicomm
sudo systemctl start agicomm
```

#### 2. 配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp nginx.conf /etc/nginx/sites-available/agicomm
sudo ln -s /etc/nginx/sites-available/agicomm /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

**访问**: http://server-ip （HTTP）或 https://server-ip （HTTPS，需配置证书）

---

## 环境变量配置

### 必需变量

```bash
# 至少配置一个 LLM API 密钥
ZHIPU_API_KEY=your_key_here        # 智谱
或
DEEPSEEK_API_KEY=your_key_here     # DeepSeek
或
OPENAI_API_KEY=your_key_here       # OpenAI
```

### 可选变量

```bash
PRIMARY_PROVIDER=zhipu             # LLM 优先级（默认：zhipu）
API_PORT=8001                      # 后端端口（默认：8001）
API_HOST=0.0.0.0                   # 后端主机（默认：0.0.0.0）
GUNICORN_WORKERS=4                 # 工作进程数（建议：CPU核数*2+1）
REQUEST_TIMEOUT=120                # 请求超时（秒）
LOG_LEVEL=INFO                     # 日志级别（DEBUG/INFO/WARNING/ERROR）
CORS_ORIGINS=*                     # CORS 允许源
```

---

## 检查部署状态

```bash
# 检查后端健康状态
curl http://server-ip:8001/health

# 预期输出：
# {"status":"ok","service":"agicomm"}

# 检查 API 文档
# 访问：http://server-ip:8001/docs

# 发送测试请求
curl -X POST http://server-ip:8001/simulate/inquiry \
  -H "Content-Type: application/json" \
  -d '{"event_text":"中国宣布在月球发现水冰"}'
```

---

## 性能优化建议

### 1. Gunicorn 参数优化

```bash
# 4 核 CPU 的推荐配置
gunicorn -w 9 \           # 工作进程: CPU核数*2+1
         -k uvicorn.workers.UvicornWorker \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --timeout 120 \
         -b 0.0.0.0:8001 \
         src.modules.api:app
```

### 2. Nginx 配置优化

```nginx
# 启用 gzip 压缩
gzip on;
gzip_types text/plain application/json;
gzip_min_length 1000;

# 连接池
upstream agicomm_backend {
    server 127.0.0.1:8000 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

### 3. 系统参数优化（Linux）

```bash
# 增加文件描述符
ulimit -n 65535

# 调整 TCP 连接参数
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

---

## 故障排查

### 问题 1: 连接被拒绝

```bash
# 检查端口是否开放
netstat -tlnp | grep 8001

# 检查防火墙
sudo ufw allow 8001

# 检查后端进程
ps aux | grep gunicorn
```

### 问题 2: 请求超时

```bash
# 增加超时时间
gunicorn --timeout 300 ...

# 检查 LLM API 响应
curl -v https://api.openai.com/v1/models
```

### 问题 3: 前端显示异常

```bash
# 检查前端构建
ls -la frontend/dist/

# 查看后端日志
tail -f gunicorn.log

# 浏览器控制台 (F12) 检查错误
```

---

## 监控与日志

### 查看日志

```bash
# Gunicorn 日志
tail -f gunicorn.log

# Nginx 访问日志
tail -f /var/log/nginx/agicomm_access.log

# Nginx 错误日志
tail -f /var/log/nginx/agicomm_error.log

# Docker 日志
docker-compose logs -f agicomm
```

### 监控指标

```bash
# 查看进程状态
ps aux | grep gunicorn

# 查看内存使用
free -h

# 查看 CPU 使用
top

# 查看网络连接
netstat -antp
```

---

## 备份与恢复

### 备份数据

```bash
# 备份配置和数据
tar -czf agicomm-backup-$(date +%Y%m%d).tar.gz \
    .env \
    data/ \
    frontend/dist/

# 上传到备份存储
```

### 恢复

```bash
# 解压备份
tar -xzf agicomm-backup-*.tar.gz

# 重启服务
systemctl restart agicomm
```

---

## 更新与维护

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新构建
bash scripts/build.sh

# 重启服务
systemctl restart agicomm
```

### 更新依赖

```bash
# 更新 Python 依赖
pip install -r requirements.txt --upgrade

# 更新前端依赖
cd frontend && npm update && cd ..

# 重新构建前端
cd frontend && npm run build && cd ..
```

---

## 常见命令速查

| 任务             | 命令                                                |
| ---------------- | --------------------------------------------------- |
| 启动开发服务器   | `python -m src.modules.api`                         |
| 启动生产服务器   | `gunicorn -w 4 -b 0.0.0.0:8001 src.modules.api:app` |
| 构建前端         | `cd frontend && npm run build`                      |
| 查看 API 文档    | http://server-ip:8001/docs                          |
| 检查健康状态     | `curl http://server-ip:8001/health`                 |
| 查看后端日志     | `tail -f gunicorn.log`                              |
| 停止 Gunicorn    | `pkill -f gunicorn`                                 |
| Docker 重启      | `docker-compose restart`                            |
| 查看 Docker 日志 | `docker-compose logs -f`                            |

---

**最后更新**: 2026-03-29
