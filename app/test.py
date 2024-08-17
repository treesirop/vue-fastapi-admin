import os
import sys
import io,time
from fastapi import FastAPI, Response, File, UploadFile, Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware  #引入 CORS中间件模块
from contextlib import asynccontextmanager
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('{}/../../..'.format(ROOT_DIR))
sys.path.append('{}/../../../third_party/Matcha-TTS'.format(ROOT_DIR))
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
import numpy as np
import torch
import torchaudio
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)

class LaunchFailed(Exception):
    pass
# 初始化模型
cosyvoice = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = os.getenv("MODEL_DIR", "pretrained_models/CosyVoice-300M-SFT")
    if model_dir:
        logging.info("MODEL_DIR is {}", model_dir)
        app.cosyvoice = CosyVoice(model_dir)
        # sft usage
        logging.info("Avaliable speakers {}", app.cosyvoice.list_avaliable_spks())
    else:
        raise LaunchFailed("MODEL_DIR environment must set")
    yield

app = FastAPI(lifespan=lifespan)

#设置允许访问的域名
origins = ["*"]  #"*"，即为所有,也可以改为允许的特定ip。
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,  #设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  #允许跨域的headers，可以用来鉴别来源等作用。

def buildResponse(output):
    buffer = io.BytesIO()
    torchaudio.save(buffer, output, 22050, format="wav")
    buffer.seek(0)
    return Response(content=buffer.read(-1), media_type="audio/wav")
# 动态加载模型的辅助函数
def load_model(model_dir):
    global cosyvoice
    try:
        cosyvoice = CosyVoice(model_dir)
        logging.info("Model loaded from {}", model_dir)
    except Exception as e:
        logging.error("Failed to load model from {}: {}", model_dir, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

# 推理接口
@app.post("/api/inference/sft")
@app.get("/api/inference/sft")
async def sft(tts: str = Form(), role: str = Form(), model_dir: str = Form("pretrained_models/CosyVoice-300M-SFT")):
    if model_dir:
        load_model(model_dir)
    start = time.process_time()
    output = cosyvoice.inference_sft(tts, role)
    end = time.process_time()
    logging.info("infer time is {} seconds", end-start)
    return buildResponse(output['tts_speech'])

@app.post("/api/inference/zero-shot")
async def zeroShot(tts: str = Form(), prompt: str = Form(), audio: UploadFile = File(), model_dir: str = Form("pretrained_models/CosyVoice-300M")):
    if model_dir:
        load_model(model_dir)
    start = time.process_time()
    prompt_speech = load_wav(audio.file, 16000)
    prompt_audio = (prompt_speech.numpy() * (2**15)).astype(np.int16).tobytes()
    prompt_speech_16k = torch.from_numpy(np.array(np.frombuffer(prompt_audio, dtype=np.int16))).unsqueeze(dim=0)
    prompt_speech_16k = prompt_speech_16k.float() / (2**15)

    output = cosyvoice.inference_zero_shot(tts, prompt, prompt_speech_16k)
    end = time.process_time()
    logging.info("infer time is {} seconds", end-start)
    return buildResponse(output['tts_speech'])

@app.post("/api/inference/cross-lingual")
async def crossLingual(tts: str = Form(), audio: UploadFile = File(), model_dir: str = Form("pretrained_models/CosyVoice-300M")):
    if model_dir:
        load_model(model_dir)
    start = time.process_time()
    prompt_speech = load_wav(audio.file, 16000)
    prompt_audio = (prompt_speech.numpy() * (2**15)).astype(np.int16).tobytes()
    prompt_speech_16k = torch.from_numpy(np.array(np.frombuffer(prompt_audio, dtype=np.int16))).unsqueeze(dim=0)
    prompt_speech_16k = prompt_speech_16k.float() / (2**15)

    output = cosyvoice.inference_cross_lingual(tts, prompt_speech_16k)
    end = time.process_time()
    logging.info("infer time is {} seconds", end-start)
    return buildResponse(output['tts_speech'])

@app.post("/api/inference/instruct")
@app.get("/api/inference/instruct")
async def instruct(tts: str = Form(), role: str = Form(), instruct: str = Form(), model_dir: str = Form("pretrained_models/CosyVoice-300M-Instruct")):
    if model_dir:
        load_model(model_dir)
    start = time.process_time()
    output = cosyvoice.inference_instruct(tts, role, instruct)
    end = time.process_time()
    logging.info("infer time is {} seconds", end-start)
    return buildResponse(output['tts_speech'])

@app.get("/api/roles")
async def roles():
    return {"roles": app.cosyvoice.list_avaliable_spks()}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang=zh-cn>
        <head>
            <meta charset=utf-8>
            <title>Api information</title>
        </head>
        <body>
            Get the supported tones from the Roles API first, then enter the tones and textual content in the TTS API for synthesis. <a href='./docs'>Documents of API</a>
        </body>
    </html>a
    """