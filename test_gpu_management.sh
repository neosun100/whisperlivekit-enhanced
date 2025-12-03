#!/bin/bash

echo "========================================="
echo "WhisperLiveKit GPU 资源管理测试"
echo "========================================="
echo ""

# 检查容器是否运行
if ! docker ps | grep -q whisperlivekit; then
    echo "❌ 容器未运行，请先启动: ./start.sh"
    exit 1
fi

echo "✓ 容器正在运行"
echo ""

# 测试 1: 验证懒加载（启动时不占用 GPU）
echo "【测试 1】验证懒加载"
echo "检查容器启动后的 GPU 显存占用..."
echo ""

gpu_mem=$(docker exec whisperlivekit nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ -n "$gpu_mem" ]; then
    echo "当前 GPU 显存占用: ${gpu_mem} MB"
    if [ "$gpu_mem" -lt 500 ]; then
        echo "✓ 懒加载正常：启动时未加载模型"
    else
        echo "⚠ 可能已加载模型（显存 > 500MB）"
    fi
else
    echo "⚠ 无法获取 GPU 信息"
fi
echo ""

# 测试 2: 检查健康状态
echo "【测试 2】检查健康状态"
health=$(curl -s http://localhost:8000/health)
if echo "$health" | grep -q "healthy"; then
    echo "✓ 服务健康"
    echo "$health" | python3 -m json.tool 2>/dev/null || echo "$health"
else
    echo "❌ 服务异常"
fi
echo ""

# 测试 3: 模拟使用（需要手动）
echo "【测试 3】模拟使用"
echo "请执行以下步骤："
echo "1. 打开浏览器访问 http://localhost:8000"
echo "2. 点击 '开始录音' 按钮"
echo "3. 说几句话"
echo "4. 点击 '停止' 按钮"
echo ""
read -p "完成后按 Enter 继续..."
echo ""

# 测试 4: 验证模型已加载
echo "【测试 4】验证模型已加载"
health=$(curl -s http://localhost:8000/health)
model_loaded=$(echo "$health" | grep -o '"model_loaded":[^,}]*' | cut -d: -f2)
gpu_mem=$(echo "$health" | grep -o '"memory_allocated_mb":[^,}]*' | cut -d: -f2)

echo "模型加载状态: $model_loaded"
echo "GPU 显存占用: $gpu_mem MB"

if echo "$model_loaded" | grep -q "true"; then
    echo "✓ 模型已加载到 GPU"
else
    echo "⚠ 模型未加载（可能需要实际使用才会加载）"
fi
echo ""

# 测试 5: 等待空闲超时
echo "【测试 5】等待空闲超时"
timeout_sec=$(echo "$health" | grep -o '"idle_timeout_seconds":[^,}]*' | cut -d: -f2)
echo "配置的超时时间: ${timeout_sec} 秒"
echo ""
echo "选项："
echo "1. 等待完整超时时间（需要 ${timeout_sec} 秒）"
echo "2. 跳过此测试"
read -p "请选择 (1/2): " choice

if [ "$choice" = "1" ]; then
    echo "等待 ${timeout_sec} 秒..."
    sleep "$timeout_sec"
    
    echo ""
    echo "检查资源是否已释放..."
    health=$(curl -s http://localhost:8000/health)
    model_loaded=$(echo "$health" | grep -o '"model_loaded":[^,}]*' | cut -d: -f2)
    
    if echo "$model_loaded" | grep -q "false"; then
        echo "✓ 资源已自动释放"
    else
        echo "⚠ 资源未释放（可能超时时间未到）"
    fi
    
    # 检查日志
    echo ""
    echo "查看释放日志："
    docker-compose logs --tail=20 whisperlivekit | grep -i "releasing\|freed" || echo "未找到释放日志"
else
    echo "跳过超时测试"
fi
echo ""

# 测试 6: 验证重新加载
echo "【测试 6】验证重新加载"
echo "请再次使用服务（打开 UI 并开始录音）"
read -p "完成后按 Enter 继续..."

health=$(curl -s http://localhost:8000/health)
model_loaded=$(echo "$health" | grep -o '"model_loaded":[^,}]*' | cut -d: -f2)

if echo "$model_loaded" | grep -q "true"; then
    echo "✓ 模型已重新加载"
else
    echo "⚠ 模型未加载"
fi

echo ""
echo "查看加载日志："
docker-compose logs --tail=20 whisperlivekit | grep -i "lazy loading\|loaded successfully" || echo "未找到加载日志"
echo ""

# 总结
echo "========================================="
echo "测试完成"
echo "========================================="
echo ""
echo "完整日志查看："
echo "  docker-compose logs -f whisperlivekit"
echo ""
echo "GPU 监控："
echo "  watch -n 1 'docker exec whisperlivekit nvidia-smi'"
echo ""
