#!/bin/bash

echo "==================================="
echo "WhisperLiveKit 网络访问测试"
echo "==================================="
echo ""

# 获取本机 IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "本机 IP: $LOCAL_IP"
echo ""

# 测试 localhost
echo "1. 测试 localhost 访问..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ localhost:8000 可访问"
else
    echo "✗ localhost:8000 不可访问"
fi

# 测试本机 IP
echo ""
echo "2. 测试本机 IP 访问..."
if curl -s http://$LOCAL_IP:8000/health > /dev/null 2>&1; then
    echo "✓ $LOCAL_IP:8000 可访问"
else
    echo "✗ $LOCAL_IP:8000 不可访问"
fi

# 检查端口监听
echo ""
echo "3. 检查端口监听状态..."
if command -v netstat > /dev/null 2>&1; then
    netstat -tuln | grep :8000 || echo "端口 8000 未监听"
elif command -v ss > /dev/null 2>&1; then
    ss -tuln | grep :8000 || echo "端口 8000 未监听"
else
    echo "无法检查端口状态（需要 netstat 或 ss 命令）"
fi

# 检查 Docker 端口映射
echo ""
echo "4. 检查 Docker 端口映射..."
docker port whisperlivekit 2>/dev/null || echo "容器未运行或端口未映射"

echo ""
echo "==================================="
echo "访问地址："
echo "  本机:     http://localhost:8000"
echo "  局域网:   http://$LOCAL_IP:8000"
echo "  API 文档: http://$LOCAL_IP:8000/docs"
echo "==================================="
