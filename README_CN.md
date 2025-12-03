<h1 align="center">WhisperLiveKit 增强版</h1>

<p align="center">
  <b>超低延迟、自托管语音转文字，智能 GPU 资源管理</b>
</p>

<p align="center">
  [English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)
</p>

<p align="center">
  <a href="https://pypi.org/project/whisperlivekit/"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/whisperlivekit?color=g"></a>
  <a href="https://pepy.tech/project/whisperlivekit"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/whisperlivekit?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=installations"></a>
  <a href="https://github.com/QuentinFuxa/WhisperLiveKit/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache%202.0-dark_green"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.9--3.15-dark_green">
</p>

<p align="center">
  <img src="demo.png" alt="Demo" width="730">
</p>

## ✨ 增强功能

这是一个生产就绪的增强版本：

- 🚀 **懒加载** - 按需加载模型，启动时 GPU 显存 = 0
- 🔄 **自动资源管理** - 空闲超时后自动释放 GPU 显存
- 🎨 **现代化 UI** - 响应式设计，支持深色/浅色主题
- 🌍 **多语言界面** - 英文、简体中文、繁体中文、日文
- 📡 **完整 API** - REST + WebSocket + Swagger 文档
- 🐋 **一键 Docker** - 自动 GPU 选择和部署
- 🔒 **网络就绪** - 可从任意 IP 访问

## 🚀 快速开始（3 步）

```bash
# 1. 配置环境
cp .env.example .env

# 2. 启动服务（自动选择最空闲的 GPU）
./start.sh

# 3. 访问服务
# UI:  http://localhost:8000
# API: http://localhost:8000/docs
```

## 📦 安装部署

### 方式一：Docker（推荐）

**前置要求：**
- Docker 20.10+
- Docker Compose 1.29+
- NVIDIA Docker runtime
- CUDA 12.0+

**快速启动：**
```bash
git clone https://github.com/yourusername/WhisperLiveKit.git
cd WhisperLiveKit
cp .env.example .env
./start.sh
```

**Docker Compose 配置：**
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

**健康检查：**
```bash
curl http://localhost:8000/health
```

### 方式二：直接安装

**前置要求：**
- Python 3.9-3.15
- CUDA 12.0+（GPU 加速）
- FFmpeg

**安装步骤：**
```bash
# 安装包
pip install whisperlivekit

# 安装可选依赖
pip install faster-whisper  # GPU 加速

# 启动服务器
wlk --model medium --language zh
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WLK_PORT` | 服务端口 | `8000` |
| `CUDA_VISIBLE_DEVICES` | GPU 选择（`auto` 自动选择） | `auto` |
| `WLK_MODEL` | 模型大小（tiny/base/small/medium/large） | `medium` |
| `WLK_LANGUAGE` | 源语言 | `auto` |
| `WLK_IDLE_TIMEOUT` | 空闲超时（分钟） | `10` |
| `WLK_DIARIZATION` | 启用说话人识别 | `false` |
| `WLK_TARGET_LANGUAGE` | 翻译目标语言 | - |

### 模型选择

| 模型 | GPU 显存 | 速度 | 质量 |
|------|---------|------|------|
| tiny | ~1 GB | 最快 | 基础 |
| base | ~1.5 GB | 快 | 良好 |
| small | ~2 GB | 中等 | 较好 |
| medium | ~5 GB | 慢 | 优秀 |
| large | ~10 GB | 最慢 | 最佳 |

## 💡 使用示例

### Web UI
1. 打开 http://localhost:8000
2. 点击"开始录音"
3. 说话并查看实时转录
4. 在设置面板配置参数

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

## 🔧 GPU 资源管理

### 懒加载
- 容器启动时 **GPU 显存 = 0 MB**
- 仅在首次请求时加载模型
- 新请求时自动重新加载

### 自动释放
- 监控空闲时间
- 超时后释放 GPU 显存（默认：10 分钟）
- 完全清空 CUDA 缓存

### 监控
```bash
# 检查健康状态
curl http://localhost:8000/health

# 监控 GPU 使用
watch -n 1 'docker exec whisperlivekit nvidia-smi'

# 查看日志
docker-compose logs -f | grep -E "lazy loading|releasing|freed"
```

## 📊 API 文档

访问 Swagger UI：http://localhost:8000/docs

### 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | Web UI |
| GET | `/health` | 健康检查（含 GPU 信息） |
| POST | `/api/transcribe` | 文件转录 |
| WS | `/asr` | 实时转录 |
| GET | `/docs` | Swagger 文档 |

## 🏗️ 项目结构

```
WhisperLiveKit/
├── docker-compose.yml          # Docker 配置
├── Dockerfile.enhanced         # 增强版 Dockerfile
├── start.sh                    # 一键启动脚本
├── .env.example               # 环境变量模板
├── whisperlivekit/
│   ├── enhanced_server.py     # 增强服务器（懒加载）
│   ├── enhanced_ui.py         # 现代化多语言 UI
│   ├── core.py                # 转录引擎
│   └── audio_processor.py     # 音频处理
├── examples/
│   └── api_client.py          # API 使用示例
└── docs/                      # 文档
```

## 🛠️ 技术栈

- **后端**：FastAPI、Uvicorn、PyTorch
- **AI 模型**：Whisper、Sortformer（说话人识别）、NLLB（翻译）
- **前端**：原生 JavaScript（无依赖）
- **部署**：Docker、Docker Compose
- **GPU**：CUDA、cuDNN

## 🧪 测试

```bash
# 运行部署测试
./test_deployment.sh

# 测试 GPU 管理
./test_gpu_management.sh

# 测试网络访问
./test_network_access.sh
```

## 📚 文档

- [快速开始](快速开始.md)
- [GPU 资源管理说明](GPU资源管理说明.md)
- [网络访问配置](网络访问配置.md)
- [部署指南](DEPLOYMENT.md)
- [功能增强说明](ENHANCEMENTS.md)

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📝 更新日志

### v1.0.0 (2025-12-03)
- ✨ 新增 GPU 资源懒加载
- ✨ 实现自动资源释放
- ✨ 新增现代化多语言 UI
- ✨ 新增完整 REST + WebSocket API
- ✨ 新增 Swagger 文档
- ✨ 自动化 GPU 选择
- ✨ 一键 Docker 部署

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

基于优秀的 [WhisperLiveKit](https://github.com/QuentinFuxa/WhisperLiveKit) 项目。

技术支持：
- [Whisper](https://github.com/openai/whisper) - OpenAI 语音识别
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - 优化推理
- [Sortformer](https://arxiv.org/abs/2507.18446) - 说话人识别
- [NLLB](https://github.com/facebookresearch/fairseq/tree/nllb) - 翻译

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/WhisperLiveKit&type=Date)](https://star-history.com/#yourusername/WhisperLiveKit)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<p align="center">用 ❤️ 为 AI 社区打造</p>
