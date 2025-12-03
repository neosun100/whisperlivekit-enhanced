#!/bin/bash

set -e

echo "==================================="
echo "WhisperLiveKit Docker Deployment"
echo "==================================="

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env file to configure your settings"
fi

# 检查 nvidia-docker
if ! docker run --rm --gpus all nvidia/cuda:12.9.1-base-ubuntu24.04 nvidia-smi &> /dev/null; then
    echo "Error: nvidia-docker is not properly configured"
    echo "Please install nvidia-docker2 and restart docker daemon"
    exit 1
fi

echo "✓ nvidia-docker is available"

# 停止旧容器
if [ "$(docker ps -aq -f name=whisperlivekit)" ]; then
    echo "Stopping existing container..."
    docker stop whisperlivekit 2>/dev/null || true
    docker rm whisperlivekit 2>/dev/null || true
fi

# 构建并启动
echo "Building and starting WhisperLiveKit..."
docker-compose up -d --build

echo ""
echo "==================================="
echo "✓ WhisperLiveKit is starting!"
echo "==================================="
echo ""
echo "Access the service at:"
echo "  UI:      http://localhost:8000"
echo "  API:     http://localhost:8000/docs"
echo "  Health:  http://localhost:8000/health"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop with:      docker-compose down"
echo ""
