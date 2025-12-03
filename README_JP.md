<h1 align="center">whisperlivekit-enhanced Enhanced</h1>

<p align="center">
  <b>超低遅延、セルフホスト音声認識、インテリジェントGPU管理</b>
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

## ✨ 拡張機能

- 🚀 **遅延読み込み** - 必要時のみモデルを読み込み、起動時GPU メモリ = 0
- 🔄 **自動リソース管理** - アイドルタイムアウト後にGPUメモリを自動解放
- 🎨 **モダンUI** - レスポンシブデザイン、ダーク/ライトテーマ対応
- 🌍 **多言語UI** - 英語、中国語（簡体字/繁体字）、日本語
- 📡 **完全なAPI** - REST + WebSocket + Swagger ドキュメント
- 🐋 **ワンクリックDocker** - 自動GPU選択とデプロイ

## 🚀 クイックスタート

```bash
# 1. 環境設定
cp .env.example .env

# 2. サービス起動
./start.sh

# 3. サービスにアクセス
# UI:  http://localhost:8000
# API: http://localhost:8000/docs
```

## 📦 インストール

### Docker（推奨）

```bash
git clone https://github.com/neosun100/whisperlivekit-enhanced.git
cd whisperlivekit-enhanced
cp .env.example .env
./start.sh
```

### 直接インストール

```bash
pip install whisperlivekit
pip install faster-whisper
wlk --model medium --language ja
```

## ⚙️ 設定

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `WLK_PORT` | サーバーポート | `8000` |
| `CUDA_VISIBLE_DEVICES` | GPU選択 | `auto` |
| `WLK_MODEL` | モデルサイズ | `medium` |
| `WLK_IDLE_TIMEOUT` | アイドルタイムアウト（分） | `10` |

## 💡 使用例

### Web UI
1. http://localhost:8000 を開く
2. 「録音開始」をクリック
3. 話すとリアルタイムで文字起こし

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

## 🔧 GPUリソース管理

- コンテナ起動時 GPU メモリ = 0 MB
- 最初のリクエスト時のみモデルを読み込み
- タイムアウト後に自動的にGPUリソースを解放

## 📊 APIドキュメント

Swagger UI: http://localhost:8000/docs

## 🛠️ 技術スタック

- **バックエンド**: FastAPI、Uvicorn、PyTorch
- **AIモデル**: Whisper、Sortformer、NLLB
- **フロントエンド**: Vanilla JavaScript
- **デプロイ**: Docker、Docker Compose

## 📚 ドキュメント

- [クイックスタート](快速开始.md)
- [GPUリソース管理](GPU资源管理说明.md)
- [デプロイガイド](DEPLOYMENT.md)

## 📄 ライセンス

Apache License 2.0 - 詳細は [LICENSE](LICENSE) ファイルを参照。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/whisperlivekit-enhanced&type=Date)](https://star-history.com/#neosun100/whisperlivekit-enhanced)

## 📱 フォローする

![QR Code](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<p align="center">AIコミュニティのために ❤️ で作成</p>
