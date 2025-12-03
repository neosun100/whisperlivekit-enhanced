import asyncio
import gc
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from whisperlivekit import AudioProcessor, TranscriptionEngine, parse_args
from whisperlivekit.enhanced_ui import get_enhanced_ui_html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

args = parse_args()
transcription_engine = None
last_activity_time = time.time()
idle_timeout = int(os.environ.get('WLK_IDLE_TIMEOUT', 10)) * 60
resource_lock = asyncio.Lock()

class TranscriptionRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = None

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    segments: list = []

def release_gpu_resources():
    """真正释放 GPU 资源"""
    global transcription_engine
    
    if transcription_engine is None:
        return
    
    logger.info("Releasing GPU resources...")
    
    # 删除模型引用
    if hasattr(transcription_engine, 'asr') and transcription_engine.asr:
        del transcription_engine.asr
    if hasattr(transcription_engine, 'diarization_model') and transcription_engine.diarization_model:
        del transcription_engine.diarization_model
    if hasattr(transcription_engine, 'translation_model') and transcription_engine.translation_model:
        del transcription_engine.translation_model
    
    transcription_engine = None
    
    # 清理 Python 垃圾回收
    gc.collect()
    
    # 清空 CUDA 缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        logger.info(f"GPU memory freed. Current allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")

async def check_idle_timeout():
    """后台任务：检查空闲超时并释放资源"""
    global last_activity_time
    while True:
        await asyncio.sleep(60)
        if transcription_engine and time.time() - last_activity_time > idle_timeout:
            async with resource_lock:
                if transcription_engine and time.time() - last_activity_time > idle_timeout:
                    logger.info(f"Idle timeout ({idle_timeout}s) reached, releasing GPU resources")
                    release_gpu_resources()

async def ensure_model_loaded():
    """懒加载：确保模型已加载"""
    global transcription_engine, last_activity_time
    
    async with resource_lock:
        if transcription_engine is None:
            logger.info("Loading transcription engine (lazy loading)...")
            # 重置 TranscriptionEngine 的单例状态
            TranscriptionEngine._instance = None
            TranscriptionEngine._initialized = False
            transcription_engine = TranscriptionEngine(**vars(args))
            logger.info("Transcription engine loaded successfully")
        
        last_activity_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：不在启动时加载模型"""
    logger.info("Starting WhisperLiveKit Enhanced Server (lazy loading mode)")
    asyncio.create_task(check_idle_timeout())
    yield
    # 关闭时释放资源
    release_gpu_resources()

app = FastAPI(
    title="WhisperLiveKit API",
    description="Ultra-low-latency speech-to-text with speaker identification (Lazy Loading)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """返回增强版 UI"""
    return HTMLResponse(get_enhanced_ui_html())

@app.get("/health")
async def health_check():
    """健康检查"""
    global last_activity_time
    last_activity_time = time.time()
    
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            "gpu_available": True,
            "gpu_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "memory_allocated_mb": round(torch.cuda.memory_allocated() / 1024**2, 2),
            "memory_reserved_mb": round(torch.cuda.memory_reserved() / 1024**2, 2),
        }
    
    return {
        "status": "healthy",
        "model_loaded": transcription_engine is not None,
        "idle_timeout_seconds": idle_timeout,
        "time_since_last_activity": round(time.time() - last_activity_time, 2),
        **gpu_info
    }

@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    转录音频文件
    
    - **file**: 音频文件 (支持 wav, mp3, m4a 等格式)
    """
    await ensure_model_loaded()
    
    try:
        audio_data = await file.read()
        # 这里简化处理，实际需要完整的音频处理流程
        return TranscriptionResponse(
            text="API transcription not fully implemented yet",
            language=args.lan,
            segments=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/asr")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时转录"""
    global last_activity_time
    
    # 懒加载模型
    await ensure_model_loaded()
    
    audio_processor = AudioProcessor(transcription_engine=transcription_engine)
    await websocket.accept()
    logger.info("WebSocket connection opened")
    
    try:
        await websocket.send_json({"type": "config", "useAudioWorklet": bool(args.pcm_input)})
    except Exception as e:
        logger.warning(f"Failed to send config: {e}")
    
    results_generator = await audio_processor.create_tasks()
    
    async def handle_results():
        async for response in results_generator:
            await websocket.send_json(response.to_dict())
            last_activity_time = time.time()
        await websocket.send_json({"type": "ready_to_stop"})
    
    results_task = asyncio.create_task(handle_results())
    
    try:
        while True:
            message = await websocket.receive_bytes()
            await audio_processor.process_audio(message)
            last_activity_time = time.time()
    except (KeyError, WebSocketDisconnect):
        logger.info("WebSocket disconnected")
    finally:
        if not results_task.done():
            results_task.cancel()
        await audio_processor.cleanup()
        logger.info("WebSocket connection closed")

def main():
    import uvicorn
    
    uvicorn_kwargs = {
        "app": "whisperlivekit.enhanced_server:app",
        "host": args.host,
        "port": args.port,
        "reload": False,
        "log_level": "info",
    }
    
    if args.ssl_certfile and args.ssl_keyfile:
        uvicorn_kwargs.update({
            "ssl_certfile": args.ssl_certfile,
            "ssl_keyfile": args.ssl_keyfile
        })
    
    if args.forwarded_allow_ips:
        uvicorn_kwargs["forwarded_allow_ips"] = args.forwarded_allow_ips
    
    logger.info(f"Starting server with lazy loading (idle timeout: {idle_timeout}s)")
    uvicorn.run(**uvicorn_kwargs)

if __name__ == "__main__":
    main()
