# WhisperLiveKit 项目结构

## 📁 新增文件清单

### Docker 部署相关
```
├── docker-compose.yml              # Docker Compose 配置
├── Dockerfile.enhanced             # 增强版 Dockerfile
├── .env.example                    # 环境变量模板
├── start.sh                        # 一键启动脚本 ⭐
├── test_deployment.sh              # 部署测试脚本
└── start_with_gpu_selection.py    # GPU 自动选择脚本
```

### 增强服务器
```
whisperlivekit/
├── enhanced_server.py              # 增强版服务器（API + 资源管理）⭐
└── enhanced_ui.py                  # 增强版 UI（多语言 + 主题）⭐
```

### 文档和示例
```
├── DEPLOYMENT.md                   # 部署文档（英文）
├── ENHANCEMENTS.md                 # 功能增强说明
├── 快速开始.md                     # 快速开始（中文）⭐
├── PROJECT_STRUCTURE.md            # 本文档
└── examples/
    └── api_client.py               # API 客户端示例
```

## 🎯 核心功能模块

### 1. GPU 自动选择 (`start_with_gpu_selection.py`)
```python
功能：
- 检测所有可用 GPU
- 选择显存占用最少的 GPU
- 支持手动指定 GPU
- 自动设置 CUDA_VISIBLE_DEVICES
```

### 2. 增强服务器 (`enhanced_server.py`)
```python
功能：
- FastAPI 应用
- WebSocket 实时转录 (/asr)
- REST API 文件转录 (/api/transcribe)
- Swagger 文档 (/docs)
- 健康检查 (/health)
- 资源自动管理（空闲超时释放）
```

### 3. 增强 UI (`enhanced_ui.py`)
```html
功能：
- 响应式设计
- 深色/浅色主题
- 多语言支持（en/zh/zh-TW/ja）
- 实时转录显示
- 参数配置面板
- 说话人标识
```

## 🔄 工作流程

```
启动流程：
1. start.sh
   ↓
2. docker-compose up
   ↓
3. start_with_gpu_selection.py
   ↓ (选择最空闲 GPU)
4. enhanced_server.py
   ↓
5. 加载 TranscriptionEngine
   ↓
6. 启动 FastAPI 服务
   ↓
7. 提供 UI + API 服务

运行时流程：
用户请求 → enhanced_server.py
           ↓
      检查资源状态
           ↓
      加载模型（如需要）
           ↓
      处理音频
           ↓
      返回转录结果
           ↓
      更新活动时间
           ↓
      空闲超时检测
           ↓
      自动释放资源（如超时）
```

## 📊 架构图

```
┌─────────────────────────────────────────────┐
│           Docker Container                  │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │     start_with_gpu_selection.py       │ │
│  │     (GPU Auto Selection)              │ │
│  └───────────────┬───────────────────────┘ │
│                  ↓                          │
│  ┌───────────────────────────────────────┐ │
│  │      enhanced_server.py               │ │
│  │  ┌─────────────────────────────────┐  │ │
│  │  │  FastAPI Application            │  │ │
│  │  │  ┌──────────┬──────────────┐    │  │ │
│  │  │  │ UI Mode  │  API Mode    │    │  │ │
│  │  │  │ (HTML)   │  (REST/WS)   │    │  │ │
│  │  │  └──────────┴──────────────┘    │  │ │
│  │  │         ↓                        │  │ │
│  │  │  ┌──────────────────────────┐   │  │ │
│  │  │  │  Resource Manager        │   │  │ │
│  │  │  │  - Idle Timeout Check    │   │  │ │
│  │  │  │  - Auto GPU Release      │   │  │ │
│  │  │  │  - Auto Model Reload     │   │  │ │
│  │  │  └──────────────────────────┘   │  │ │
│  │  └─────────────────────────────────┘  │ │
│  │                  ↓                     │ │
│  │  ┌─────────────────────────────────┐  │ │
│  │  │   TranscriptionEngine           │  │ │
│  │  │   (Original WhisperLiveKit)     │  │ │
│  │  │   - Whisper Model               │  │ │
│  │  │   - Diarization                 │  │ │
│  │  │   - Translation                 │  │ │
│  │  └─────────────────────────────────┘  │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │         GPU (Auto Selected)           │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## 🔌 API 端点

### WebSocket
- `ws://host:8000/asr` - 实时转录

### REST API
- `GET  /` - UI 界面
- `GET  /health` - 健康检查
- `POST /api/transcribe` - 文件转录
- `GET  /docs` - Swagger 文档
- `GET  /openapi.json` - OpenAPI 规范

## 🌐 多语言支持

### UI 语言
- English (en)
- 简体中文 (zh)
- 繁體中文 (zh-TW)
- 日本語 (ja)

### 转录语言
支持 Whisper 的所有语言（200+）

## 🎨 主题支持

- Light Mode (浅色主题)
- Dark Mode (深色主题)
- 自动适应系统主题

## 📦 依赖关系

```
Docker
├── nvidia-docker2
├── CUDA 12.9.1
└── cuDNN

Python
├── FastAPI
├── Uvicorn
├── WebSockets
├── PyTorch
├── faster-whisper
└── whisperlivekit (原项目)
```

## 🔐 安全考虑

- CORS 已配置为允许所有来源（生产环境需调整）
- 支持 SSL/TLS（通过环境变量配置）
- 支持反向代理（forwarded_allow_ips）
- 资源自动释放防止内存泄漏

## 📈 性能优化

1. **GPU 自动选择** - 避免 GPU 资源冲突
2. **资源自动释放** - 空闲时释放 GPU 内存
3. **模型缓存** - HuggingFace 模型持久化
4. **异步处理** - FastAPI 异步架构
5. **WebSocket 连接** - 低延迟实时通信

## 🧪 测试覆盖

- [x] 健康检查端点
- [x] UI 可访问性
- [x] API 文档可访问性
- [x] WebSocket 连接
- [x] GPU 自动选择
- [x] 资源自动释放
- [x] 多语言切换
- [x] 主题切换

## 📝 配置文件

### .env
```bash
WLK_PORT=8000
CUDA_VISIBLE_DEVICES=auto
WLK_MODEL=medium
WLK_LANGUAGE=auto
WLK_IDLE_TIMEOUT=10
WLK_DIARIZATION=false
WLK_TARGET_LANGUAGE=
```

### docker-compose.yml
- 服务定义
- GPU 资源配置
- 卷挂载
- 环境变量

## 🚀 部署选项

### 开发环境
```bash
./start.sh
```

### 生产环境
```bash
# 使用 nginx 反向代理
# 配置 SSL 证书
# 设置资源限制
# 启用日志收集
```

## 📚 相关文档

- [快速开始.md](快速开始.md) - 中文快速开始
- [DEPLOYMENT.md](DEPLOYMENT.md) - 详细部署指南
- [ENHANCEMENTS.md](ENHANCEMENTS.md) - 功能增强说明
- [README.md](README.md) - 原项目文档
