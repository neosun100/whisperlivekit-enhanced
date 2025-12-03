#!/usr/bin/env python3
"""
WhisperLiveKit API 客户端示例
"""
import asyncio
import json
import websockets
import requests

# WebSocket 实时转录示例
async def websocket_example():
    """WebSocket 实时转录"""
    uri = "ws://localhost:8000/asr"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # 接收配置
        config = await websocket.recv()
        print(f"Config: {config}")
        
        # 这里应该发送音频数据
        # await websocket.send(audio_bytes)
        
        # 接收转录结果
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'transcript':
                print(f"Transcript: {data.get('text')}")
            elif data.get('type') == 'ready_to_stop':
                break

# REST API 示例
def rest_api_example():
    """REST API 文件转录"""
    url = "http://localhost:8000/api/transcribe"
    
    # 上传音频文件
    with open("audio.wav", "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Transcription: {result['text']}")
    else:
        print(f"Error: {response.status_code}")

# 健康检查示例
def health_check():
    """检查服务健康状态"""
    response = requests.get("http://localhost:8000/health")
    print(f"Health: {response.json()}")

if __name__ == "__main__":
    # 健康检查
    health_check()
    
    # WebSocket 示例
    # asyncio.run(websocket_example())
    
    # REST API 示例
    # rest_api_example()
