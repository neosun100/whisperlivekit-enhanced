#!/usr/bin/env python3
import os
import subprocess
import sys

def get_gpu_memory_usage():
    """获取所有 GPU 的显存使用情况"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,memory.used', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, check=True
        )
        gpus = []
        for line in result.stdout.strip().split('\n'):
            idx, mem = line.split(',')
            gpus.append((int(idx.strip()), int(mem.strip())))
        return gpus
    except Exception as e:
        print(f"Error querying GPU: {e}", file=sys.stderr)
        return [(0, 0)]

def select_best_gpu():
    """选择显存占用最少的 GPU"""
    gpus = get_gpu_memory_usage()
    best_gpu = min(gpus, key=lambda x: x[1])
    print(f"Available GPUs: {gpus}")
    print(f"Selected GPU {best_gpu[0]} with {best_gpu[1]}MB used")
    return str(best_gpu[0])

if __name__ == "__main__":
    cuda_devices = os.environ.get('CUDA_VISIBLE_DEVICES', 'auto')
    
    if cuda_devices == 'auto':
        selected_gpu = select_best_gpu()
        os.environ['CUDA_VISIBLE_DEVICES'] = selected_gpu
        print(f"Auto-selected GPU: {selected_gpu}")
    else:
        print(f"Using manually specified GPU(s): {cuda_devices}")
    
    # 构建启动命令
    cmd = [
        'python3', '-m', 'whisperlivekit.enhanced_server',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--model', os.environ.get('WLK_MODEL', 'medium'),
        '--language', os.environ.get('WLK_LANGUAGE', 'auto'),
    ]
    
    if os.environ.get('WLK_DIARIZATION', 'false').lower() == 'true':
        cmd.append('--diarization')
    
    if os.environ.get('WLK_TARGET_LANGUAGE'):
        cmd.extend(['--target-language', os.environ['WLK_TARGET_LANGUAGE']])
    
    print(f"Starting server with command: {' '.join(cmd)}")
    os.execvp(cmd[0], cmd)
