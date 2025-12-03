<h1 align="center">whisperlivekit-enhanced Enhanced</h1>

<p align="center">
  <b>Ultra-low-latency, self-hosted speech-to-text with intelligent GPU management</b>
</p>

<p align="center">
  [English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)
</p>

<p align="center">
  <a href="https://pypi.org/project/whisperlivekit/"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/whisperlivekit?color=g"></a>
  <a href="https://pepy.tech/project/whisperlivekit"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/whisperlivekit?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=installations"></a>
  <a href="https://github.com/QuentinFuxa/whisperlivekit-enhanced/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-dark_green"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.9--3.15-dark_green">
</p>

<p align="center">
  <img src="demo.png" alt="Demo" width="730">
</p>

## ✨ Enhanced Features

This is an enhanced version with production-ready features:

- 🚀 **Lazy Loading** - Models load only when needed, GPU memory = 0 at startup
- 🔄 **Auto Resource Management** - Automatic GPU memory release after idle timeout
- 🎨 **Modern UI** - Responsive design with dark/light themes
- 🌍 **Multi-language UI** - English, Chinese (Simplified/Traditional), Japanese
- 📡 **Complete API** - REST + WebSocket + Swagger documentation
- 🐋 **One-Click Docker** - Automated GPU selection and deployment
- 🔒 **Network Ready** - Accessible from any IP address

## 🚀 Quick Start (3 Steps)

```bash
# 1. Configure environment
cp .env.example .env

# 2. Start service (auto-selects least busy GPU)
./start.sh

# 3. Access service
# UI:  http://localhost:8000
# API: http://swagger:8000/docs
```

## 📦 Installation

### Method 1: Docker (Recommended)

**Prerequisites:**
- Docker 20.10+
- Docker Compose 1.29+
- NVIDIA Docker runtime
- CUDA 12.0+

**Quick Start:**
```bash
git clone https://github.com/neosun100/whisperlivekit-enhanced.git
cd whisperlivekit-enhanced
cp .env.example .env
./start.sh
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  whisperlivekit:
    image: whisperlivekit:latest
    ports:
      - "0.0.0.0:8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=auto
      - WLK_MODEL=medium
      - WLK_IDLE_TIMEOUT=10
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

### Method 2: Direct Installation

**Prerequisites:**
- Python 3.9-3.15
- CUDA 12.0+ (for GPU)
- FFmpeg

**Installation:**
```bash
# Install package
pip install whisperlivekit

# Install optional dependencies
pip install faster-whisper  # For GPU acceleration

# Start server
wlk --model medium --language en
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WLK_PORT` | Server port | `8000` |
| `CUDA_VISIBLE_DEVICES` | GPU selection (`auto` for automatic) | `auto` |
| `WLK_MODEL` | Model size (tiny/base/small/medium/large) | `medium` |
| `WLK_LANGUAGE` | Source language | `auto` |
| `WLK_IDLE_TIMEOUT` | Idle timeout in minutes | `10` |
| `WLK_DIARIZATION` | Enable speaker diarization | `false` |
| `WLK_TARGET_LANGUAGE` | Translation target language | - |

### Model Selection

| Model | GPU Memory | Speed | Quality |
|-------|-----------|-------|---------|
| tiny | ~1 GB | Fastest | Basic |
| base | ~1.5 GB | Fast | Good |
| small | ~2 GB | Medium | Better |
| medium | ~5 GB | Slow | Great |
| large | ~10 GB | Slowest | Best |

## 💡 Usage Examples

### Web UI
1. Open http://localhost:8000
2. Click "Start Recording"
3. Speak and see real-time transcription
4. Configure parameters in settings panel

### Python API
```python
import asyncio
import websockets
import json

async def transcribe():
    uri = "ws://localhost:8000/asr"
    async with websockets.connect(uri) as ws:
        async for message in ws:
            data = json.loads(message)
            if data.get('type') == 'transcript':
                print(data['text'])

asyncio.run(transcribe())
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.wav"
```

## 🔧 GPU Resource Management

### Lazy Loading
- Container starts with **0 MB GPU memory**
- Models load only on first request
- Automatic reload on new requests

### Auto Release
- Monitors idle time
- Releases GPU memory after timeout (default: 10 minutes)
- Clears CUDA cache completely

### Monitoring
```bash
# Check health status
curl http://localhost:8000/health

# Monitor GPU usage
watch -n 1 'docker exec whisperlivekit nvidia-smi'

# View logs
docker-compose logs -f | grep -E "lazy loading|releasing|freed"
```

## 📊 API Documentation

Access Swagger UI at: http://localhost:8000/docs

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/health` | Health check with GPU info |
| POST | `/api/transcribe` | File transcription |
| WS | `/asr` | Real-time transcription |
| GET | `/docs` | Swagger documentation |

## 🏗️ Project Structure

```
whisperlivekit-enhanced/
├── docker-compose.yml          # Docker configuration
├── Dockerfile.enhanced         # Enhanced Dockerfile
├── start.sh                    # One-click startup
├── .env.example               # Environment template
├── whisperlivekit/
│   ├── enhanced_server.py     # Enhanced server with lazy loading
│   ├── enhanced_ui.py         # Modern multi-language UI
│   ├── core.py                # Transcription engine
│   └── audio_processor.py     # Audio processing
├── examples/
│   └── api_client.py          # API usage examples
└── docs/                      # Documentation
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn, PyTorch
- **AI Models**: Whisper, Sortformer (diarization), NLLB (translation)
- **Frontend**: Vanilla JavaScript (no dependencies)
- **Deployment**: Docker, Docker Compose
- **GPU**: CUDA, cuDNN

## 🧪 Testing

```bash
# Run deployment tests
./test_deployment.sh

# Test GPU management
./test_gpu_management.sh

# Test network access
./test_network_access.sh
```

## 📚 Documentation

- [Quick Start (Chinese)](快速开始.md)
- [GPU Resource Management](GPU资源管理说明.md)
- [Network Configuration](网络访问配置.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Enhancements](ENHANCEMENTS.md)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 Changelog

### v1.0.0 (2025-12-03)
- ✨ Added lazy loading for GPU resources
- ✨ Implemented automatic resource release
- ✨ Added modern multi-language UI
- ✨ Added complete REST + WebSocket API
- ✨ Added Swagger documentation
- ✨ Automated GPU selection
- ✨ One-click Docker deployment

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Based on the excellent [whisperlivekit-enhanced](https://github.com/QuentinFuxa/whisperlivekit-enhanced) project.

Powered by:
- [Whisper](https://github.com/openai/whisper) - OpenAI's speech recognition
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized inference
- [Sortformer](https://arxiv.org/abs/2507.18446) - Speaker diarization
- [NLLB](https://github.com/facebookresearch/fairseq/tree/nllb) - Translation

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/whisperlivekit-enhanced&type=Date)](https://star-history.com/#neosun100/whisperlivekit-enhanced)

## 📱 Follow Us

![QR Code](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<p align="center">Made with ❤️ for the AI community</p>
