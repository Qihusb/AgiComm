# AgiComm

> Agent-driven International Communication Simulation Framework

## 1. Introduction

AgiComm is a generative agent-based simulation framework designed to model international communication dynamics...

## 2. Key Features

- Media Questioning Simulation
- News Reconstruction
- Social Dissemination

## 3. Architecture

AgiComm consists of three independent modules:

- Media Inquiring Module
- News Reconstruction Module
- Social Dissemination Module

Each module can be executed independently to avoid error propagation.

## 4. Project Structure

```bash
src/                # core logic
configs/            # prompts & parameters
experiments/        # runnable scripts
data/               # dataset (not included)
```

## 5. Quick Start

```bash
git clone https://github.com/Qihusb/AgiComm.git
cd AgiComm
pip install -r requirements.txt
```

## 6. Experiments

### 6.1 Media Inquiring API Usage (2026.03)

- See `docs/api_guide_media_inquiry.md` for detailed API and frontend usage, including:
  - How to use `media_ids` for multi-media selection (max 20)
  - Streaming response support for real-time frontend display
  - Health check endpoint and error handling
  - Frontend integration best practices (progress bar, error tips, etc.)

## 7. Production Deployment

For production server deployment and detailed deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

Quick start options:
- **Linux/macOS**: `bash scripts/build.sh`
- **Windows**: `scripts\build.bat`
- **Docker**: `docker-compose up -d`
- **Nginx + Gunicorn**: See deployment guide for systemd setup

Key deployment features:
- ✅ One-command build automation for both Linux and Windows
- ✅ Docker containerization with health checks
- ✅ Nginx reverse proxy configuration with HTTPS support
- ✅ Production environment templates (.env.production.example)
- ✅ Static file serving for frontend distribution

---

## 8. Citation
