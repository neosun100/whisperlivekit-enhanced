#!/bin/bash

echo "Testing WhisperLiveKit Deployment..."
echo ""

# 等待服务启动
echo "Waiting for service to start..."
sleep 5

# 测试健康检查
echo "1. Testing health endpoint..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

# 测试 UI
echo ""
echo "2. Testing UI endpoint..."
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$status" = "200" ]; then
    echo "✓ UI accessible"
else
    echo "✗ UI not accessible (HTTP $status)"
    exit 1
fi

# 测试 API 文档
echo ""
echo "3. Testing API docs..."
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$status" = "200" ]; then
    echo "✓ API docs accessible"
else
    echo "✗ API docs not accessible (HTTP $status)"
    exit 1
fi

echo ""
echo "==================================="
echo "✓ All tests passed!"
echo "==================================="
echo ""
echo "Access the service at:"
echo "  UI:  http://localhost:8000"
echo "  API: http://localhost:8000/docs"
echo ""
