<h1 align="center">whisperlivekit-enhanced 增強版</h1>

<p align="center">
  <b>超低延遲、自託管語音轉文字，智慧 GPU 資源管理</b>
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

## ✨ 增強功能

- 🚀 **懶載入** - 按需載入模型，啟動時 GPU 顯存 = 0
- 🔄 **自動資源管理** - 閒置逾時後自動釋放 GPU 顯存
- 🎨 **現代化 UI** - 響應式設計，支援深色/淺色主題
- 🌍 **多語言介面** - 英文、簡體中文、繁體中文、日文
- 📡 **完整 API** - REST + WebSocket + Swagger 文件
- 🐋 **一鍵 Docker** - 自動 GPU 選擇和部署

## 🚀 快速開始

```bash
# 1. 配置環境
cp .env.example .env

# 2. 啟動服務
./start.sh

# 3. 訪問服務
# UI:  http://localhost:8000
# API: http://localhost:8000/docs
```

## 📦 安裝部署

### Docker（推薦）

```bash
git clone https://github.com/neosun100/whisperlivekit-enhanced.git
cd whisperlivekit-enhanced
cp .env.example .env
./start.sh
```

### 直接安裝

```bash
pip install whisperlivekit
pip install faster-whisper
wlk --model medium --language zh
```

## ⚙️ 配置說明

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `WLK_PORT` | 服務埠 | `8000` |
| `CUDA_VISIBLE_DEVICES` | GPU 選擇 | `auto` |
| `WLK_MODEL` | 模型大小 | `medium` |
| `WLK_IDLE_TIMEOUT` | 閒置逾時（分鐘） | `10` |

## 💡 使用示例

### Web UI
1. 開啟 http://localhost:8000
2. 點擊「開始錄音」
3. 說話並查看即時轉錄

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

## 🔧 GPU 資源管理

- 容器啟動時 GPU 顯存 = 0 MB
- 僅在首次請求時載入模型
- 逾時後自動釋放 GPU 資源

## 📊 API 文件

訪問 Swagger UI：http://localhost:8000/docs

## 🛠️ 技術棧

- **後端**：FastAPI、Uvicorn、PyTorch
- **AI 模型**：Whisper、Sortformer、NLLB
- **前端**：原生 JavaScript
- **部署**：Docker、Docker Compose

## 📚 文件

- [快速開始](快速开始.md)
- [GPU 資源管理說明](GPU资源管理说明.md)
- [部署指南](DEPLOYMENT.md)

## 📄 授權

Apache License 2.0 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/whisperlivekit-enhanced&type=Date)](https://star-history.com/#neosun100/whisperlivekit-enhanced)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<p align="center">用 ❤️ 為 AI 社群打造</p>
