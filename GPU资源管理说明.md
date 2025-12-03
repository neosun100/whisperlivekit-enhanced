# WhisperLiveKit GPU 资源管理机制

## ✅ 已实现完整的懒加载和资源释放

### 核心机制

#### 1. 懒加载（Lazy Loading）
**不在容器启动时加载模型，只在首次请求时加载**

```python
async def ensure_model_loaded():
    """懒加载：确保模型已加载"""
    global transcription_engine
    
    async with resource_lock:
        if transcription_engine is None:
            logger.info("Loading transcription engine (lazy loading)...")
            # 重置单例状态
            TranscriptionEngine._instance = None
            TranscriptionEngine._initialized = False
            # 加载模型到 GPU
            transcription_engine = TranscriptionEngine(**vars(args))
            logger.info("Transcription engine loaded successfully")
```

**触发时机**：
- 首次 WebSocket 连接 (`/asr`)
- 首次 API 调用 (`/api/transcribe`)

#### 2. 自动资源释放
**空闲超时后自动释放 GPU 显存**

```python
def release_gpu_resources():
    """真正释放 GPU 资源"""
    global transcription_engine
    
    # 删除模型引用
    if hasattr(transcription_engine, 'asr'):
        del transcription_engine.asr
    if hasattr(transcription_engine, 'diarization_model'):
        del transcription_engine.diarization_model
    if hasattr(transcription_engine, 'translation_model'):
        del transcription_engine.translation_model
    
    transcription_engine = None
    
    # 清理 Python 垃圾回收
    gc.collect()
    
    # 清空 CUDA 缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
```

**释放内容**：
- ✅ Whisper ASR 模型
- ✅ 说话人识别模型（如启用）
- ✅ 翻译模型（如启用）
- ✅ Python 对象引用
- ✅ CUDA 缓存

#### 3. 空闲超时检测
**后台任务持续监控，超时自动释放**

```python
async def check_idle_timeout():
    """后台任务：检查空闲超时并释放资源"""
    while True:
        await asyncio.sleep(60)  # 每分钟检查一次
        if transcription_engine and time.time() - last_activity_time > idle_timeout:
            async with resource_lock:
                logger.info(f"Idle timeout ({idle_timeout}s) reached")
                release_gpu_resources()
```

**活动更新时机**：
- WebSocket 接收音频数据
- WebSocket 发送转录结果
- API 调用
- 健康检查

---

## 🔄 完整工作流程

### 场景 1：首次使用

```
1. 容器启动
   └─> 不加载模型（GPU 显存 = 0）

2. 用户访问 UI
   └─> 只返回 HTML（GPU 显存 = 0）

3. 用户点击"开始录音"
   └─> WebSocket 连接
   └─> 触发 ensure_model_loaded()
   └─> 加载模型到 GPU（GPU 显存 ≈ 2-8GB，取决于模型大小）
   └─> 开始实时转录

4. 用户停止录音
   └─> 记录最后活动时间
   └─> 模型保持在 GPU（等待下次使用）
```

### 场景 2：空闲超时

```
1. 最后一次活动后 10 分钟（默认）
   └─> check_idle_timeout() 检测到超时
   └─> 调用 release_gpu_resources()
   └─> 删除所有模型引用
   └─> gc.collect() 清理 Python 对象
   └─> torch.cuda.empty_cache() 清空 CUDA 缓存
   └─> GPU 显存释放（GPU 显存 ≈ 0）

2. 下次用户使用
   └─> 重新触发懒加载
   └─> 重新加载模型到 GPU
```

### 场景 3：多用户并发

```
1. 用户 A 连接
   └─> 加载模型（如未加载）
   └─> 开始转录

2. 用户 B 连接（模型已加载）
   └─> 直接使用已加载的模型
   └─> 共享 GPU 资源

3. 所有用户断开 10 分钟后
   └─> 自动释放 GPU 资源
```

---

## 📊 GPU 显存使用情况

### 不同模型的显存占用

| 模型 | 显存占用 | 加载时间 |
|------|---------|---------|
| tiny | ~1 GB | ~5 秒 |
| base | ~1.5 GB | ~8 秒 |
| small | ~2 GB | ~10 秒 |
| medium | ~5 GB | ~15 秒 |
| large | ~10 GB | ~30 秒 |

### 启用说话人识别额外占用
- Sortformer: +1-2 GB
- Diart: +2-3 GB

### 启用翻译额外占用
- NLLB 600M: +2 GB
- NLLB 1.3B: +4 GB

---

## 🔍 监控和验证

### 1. 查看健康状态
```bash
curl http://localhost:8000/health
```

**返回示例**：
```json
{
  "status": "healthy",
  "model_loaded": false,  // 模型是否已加载
  "idle_timeout_seconds": 600,
  "time_since_last_activity": 125.5,
  "gpu_available": true,
  "gpu_count": 1,
  "current_device": 0,
  "memory_allocated_mb": 0.0,  // 当前 GPU 显存占用
  "memory_reserved_mb": 0.0
}
```

### 2. 实时监控 GPU
```bash
# 在容器内
docker exec whisperlivekit nvidia-smi

# 持续监控
watch -n 1 'docker exec whisperlivekit nvidia-smi'
```

### 3. 查看日志
```bash
docker-compose logs -f whisperlivekit
```

**关键日志**：
```
Loading transcription engine (lazy loading)...
Transcription engine loaded successfully
Idle timeout (600s) reached, releasing GPU resources
GPU memory freed. Current allocated: 0.00 MB
```

---

## ⚙️ 配置参数

### 环境变量
```bash
# .env 文件
WLK_IDLE_TIMEOUT=10  # 空闲超时（分钟）
```

### 调整建议

| 使用场景 | 推荐超时 | 说明 |
|---------|---------|------|
| 频繁使用 | 30-60 分钟 | 减少重新加载次数 |
| 偶尔使用 | 5-10 分钟 | 快速释放资源 |
| 多 GPU 共享 | 3-5 分钟 | 让其他服务使用 GPU |
| 单独使用 | 不限制 | 设置很大的值 |

---

## 🧪 测试验证

### 测试 1：验证懒加载
```bash
# 1. 启动容器
./start.sh

# 2. 立即检查 GPU（应该为空）
docker exec whisperlivekit nvidia-smi

# 3. 访问 UI 并开始录音
# 浏览器打开 http://localhost:8000

# 4. 再次检查 GPU（应该有显存占用）
docker exec whisperlivekit nvidia-smi
```

### 测试 2：验证资源释放
```bash
# 1. 使用服务后停止
# 2. 等待超时时间（默认 10 分钟）
# 3. 查看日志
docker-compose logs -f | grep "releasing GPU"

# 4. 检查 GPU（应该释放）
docker exec whisperlivekit nvidia-smi
```

### 测试 3：验证重新加载
```bash
# 1. 资源释放后
# 2. 再次使用服务
# 3. 查看日志（应该看到 "lazy loading"）
docker-compose logs -f | grep "lazy loading"
```

---

## 💡 优化建议

### 1. 根据使用模式调整超时
```bash
# 高频使用：延长超时
WLK_IDLE_TIMEOUT=60

# 低频使用：缩短超时
WLK_IDLE_TIMEOUT=3
```

### 2. 选择合适的模型
```bash
# GPU 显存有限：使用小模型
WLK_MODEL=tiny

# 追求质量：使用大模型
WLK_MODEL=large
```

### 3. 按需启用功能
```bash
# 不需要说话人识别
WLK_DIARIZATION=false

# 不需要翻译
WLK_TARGET_LANGUAGE=
```

---

## ✅ 功能确认

- ✅ **懒加载**：容器启动时不加载模型
- ✅ **首次请求加载**：第一次使用时才加载到 GPU
- ✅ **空闲超时检测**：后台任务持续监控
- ✅ **自动释放**：超时后自动释放 GPU 显存
- ✅ **真正释放**：使用 `torch.cuda.empty_cache()` 清空缓存
- ✅ **自动重载**：下次使用时自动重新加载
- ✅ **线程安全**：使用 asyncio.Lock 防止竞态条件
- ✅ **状态监控**：健康检查接口显示详细状态

---

## 🎯 总结

当前实现的 GPU 资源管理机制：

1. **完全懒加载** - 容器启动时 GPU 显存为 0
2. **按需加载** - 只在首次请求时加载模型
3. **自动释放** - 空闲超时后完全释放 GPU 资源
4. **自动重载** - 新请求时自动重新加载
5. **可配置** - 超时时间可通过环境变量调整
6. **可监控** - 提供健康检查接口查看状态

**适用于多 GPU 环境，多个服务共享 GPU 资源的场景！** ✅
