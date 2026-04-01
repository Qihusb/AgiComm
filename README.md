# AgiComm

> Agent-driven International Communication Simulation Framework

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/frontend-Vue3%2B-green.svg)](https://vuejs.org/)

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

**AgiComm** is a generative agent-based simulation framework for modeling international communication dynamics, focusing on media questioning, news reconstruction, and social dissemination. It supports multi-agent, multi-language, and multi-country simulation, enabling research and application in computational communication, AI-driven media studies, and digital diplomacy.

---

## Features

- 🌍 **Media Questioning Simulation**: Simulate 116 global media's reactions to science/diplomacy events, with customizable selection and batch calls.
- ⚡ **Streaming Response**: Real-time, chunked JSON output for frontend progress display.
- 🧩 **Error Detection**: Built-in anomaly detection and user-friendly error tips.
- 🟢 **Health Monitoring**: Real backend health check endpoint and frontend status indicator.
- 🛠️ **One-Command Deployment**: Linux, Windows, Docker, Nginx, and production-ready scripts.
- 🔒 **Configurable & Secure**: Environment variable templates, CORS, and API key management.
- 📄 **Comprehensive Documentation**: API usage, deployment, and troubleshooting guides.

---

## Architecture

AgiComm consists of three independent modules:

- **Media Inquiring Module**: Multi-media, multi-country event simulation.
- **News Reconstruction Module**: (Planned) Automated news rewriting and summarization.
- **Social Dissemination Module**: (Planned) Social network propagation simulation.

Each module can be executed independently to avoid error propagation.

---

## Project Structure

```text
src/                # Core backend logic (FastAPI)
frontend/           # Vue3 + Vite frontend
configs/            # Prompts & parameters
data/               # Datasets (not included)
experiments/        # Experimental scripts
docs/               # API and usage documentation
scripts/            # Build, start, and health check scripts
```

---

## Installation

### Requirements

- Python 3.8+
- Node.js 16+ (for frontend)
- npm or yarn
- Git (optional, for cloning)

### Backend

```bash
git clone https://github.com/Qihusb/AgiComm.git
cd AgiComm
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

---

## Quick Start

### Development

```bash
# Start backend (dev)
python -m src.modules.api

# Start frontend (dev)
cd frontend && npm run dev
```

### Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

- **Linux/macOS**: `bash scripts/build.sh`
- **Windows**: `scripts\build.bat`
- **Docker**: `docker-compose up -d`
- **Nginx + Gunicorn**: See deployment guide for systemd setup

---

## API Usage

See [docs/api_guide_media_inquiry.md](docs/api_guide_media_inquiry.md) for full API details.

- **Endpoint**: `POST /simulate/inquiry`
- **Request**: `{ "event_text": "...", "media_ids": [...] }`
- **Response**: Streaming JSON (one media per chunk)
- **Health Check**: `GET /health`
- **API Docs**: `/docs` (if enabled)

Example:

```bash
curl -X POST http://server-ip:8001/simulate/inquiry \
  -H "Content-Type: application/json" \
  -d '{"event_text":"中国宣布在月球发现水冰"}'
```

---

## Production Deployment

- One-command build scripts for Linux/macOS and Windows
- Docker and Docker Compose support
- Nginx reverse proxy configuration
- Environment variable templates (`.env.example`)
- Static file serving for frontend distribution

See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

---

## Contributing

Contributions are welcome! Please open issues or pull requests for bug reports, feature requests, or documentation improvements.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

---

## Citation

If you use AgiComm in your research, please cite:

```
@software{agicomm2026,
  author = {Qihusb et al.},
  title = {AgiComm: Agent-driven International Communication Simulation Framework},
  year = {2026},
  url = {https://github.com/Qihusb/AgiComm}
}
```

---

**Contact**: For questions or collaboration, please open an issue or contact the maintainer.

---

如需中文部署说明、API 细节和常见问题，请参见 [DEPLOYMENT.md](DEPLOYMENT.md) 和 [docs/api_guide_media_inquiry.md](docs/api_guide_media_inquiry.md)。
