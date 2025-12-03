# WhisperLiveKit Docker 部署指南

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置参数
```

### 2. 一键启动

```bash
./start.sh
```

### 3. 访问服务

- **UI 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 功能特性

### ✅ 自动 GPU 选择
每次启动自动选择显存占用最少的 GPU

### ✅ 双模式支持
- **UI 模式**: 现代化响应式界面，支持深色模式
- **API 模式**: RESTful API + WebSocket，完整 Swagger 文档

### ✅ 资源自动管理
空闲 N 分钟后自动释放 GPU 资源，新请求时自动重新加载

### ✅ 多语言支持
UI 支持英文、简体中文、繁体中文、日文

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| WLK_PORT | 服务端口 | 8000 |
| CUDA_VISIBLE_DEVICES | GPU 选择 (auto 自动选择) | auto |
| WLK_MODEL | 模型大小 | medium |
| WLK_LANGUAGE | 源语言 | auto |
| WLK_IDLE_TIMEOUT | 空闲超时(分钟) | 10 |
| WLK_DIARIZATION | 启用说话人识别 | false |
| WLK_TARGET_LANGUAGE | 翻译目标语言 | - |

## API 使用

### WebSocket 实时转录

```javascript
const ws = new WebSocket('ws://localhost:8000/asr');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.text);
};
```

### REST API 文件转录

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.wav"
```

## 管理命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看 GPU 使用
docker exec whisperlivekit nvidia-smi
```

## 故障排查

### GPU 不可用
```bash
# 检查 nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.9.1-base-ubuntu24.04 nvidia-smi
```

### 端口被占用
修改 .env 中的 WLK_PORT

### 模型下载慢
使用 HuggingFace 镜像或预下载模型
