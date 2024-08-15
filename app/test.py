import io
from fastapi import FastAPI, Response
import torchaudio
import torch
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/generate_audio")
async def generate_audio():
    # 创建一个简单的音频信号，这里是一个1秒钟的440Hz正弦波
    sample_rate = 22050
    duration = 1  # seconds
    frequency = 440  # Hz

    t = torch.linspace(0, duration, int(sample_rate * duration))
    audio_signal = 0.5 * torch.sin(2 * torch.pi * frequency * t)

    # 将音频信号保存到内存缓冲区
    buffer = io.BytesIO()
    torchaudio.save(buffer, audio_signal.unsqueeze(0), sample_rate, format="wav")
    buffer.seek(0)

    # 返回音频响应
    return Response(content=buffer.read(), media_type="audio/wav")

def main():
    uvicorn.run(app, host="0.0.0.0", port=8888)

if __name__ == "__main__":
    main()