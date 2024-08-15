import logging
import uuid

from fastapi import APIRouter, Body, File, HTTPException, Query,Form, UploadFile
from fastapi.responses import FileResponse
import httpx
from tortoise.expressions import Q

from app.controllers.audio import audio_controller
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.audio import *
from dotenv import load_dotenv
import os

load_dotenv() 
logger = logging.getLogger(__name__)
server_ip_cosy = os.getenv('SERVER_IP_COSY')
temp_audio_save_path = os.getenv('TEMP_AUDIO_SAVE_PATH')
final_audio_save_path=os.getenv('FINAL_AUDIO_SAVE_PATH') 
router = APIRouter()
if not os.path.exists(temp_audio_save_path):
    os.makedirs(temp_audio_save_path)
if not os.path.exists(final_audio_save_path):
    os.makedirs(final_audio_save_path) 
    
# 鉴权暂时移除  
@router.get("/audio_list",summary="获取音频列表")
async def audio_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_id: int= Query(1, description="用户id"),
    cloned_voice: bool = Query(False,description="音频标识")
):
    q = Q()
    if user_id:
        q &= Q(user_id=user_id)
    if cloned_voice is not None:
        q &= Q(cloned_voice=cloned_voice)
    total, user_objs = await audio_controller.list(page=page, page_size=page_size, search=q)
    data = [await obj.to_dict(m2m=True) for obj in user_objs]

    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/generate_sft", summary="sft生成音频")
async def generate_audio(
    tts: str = Form(...),
    role: str = Form(default="中文女")
):
    # url = f"https://{server_ip_cosy}/api/inference/sft"
    url = "http://127.0.0.1:8888/generate_audio"
    payload = {
        'tts': tts,
        'role': role
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(url) #data=payload
            response.raise_for_status()
            audio_content = response.content
            
            # 生成唯一的文件名
            file_id = str(uuid.uuid4())
            temp_file_name = f"{file_id}.wav"
            temp_file_path = os.path.join(temp_audio_save_path, temp_file_name)
            
            # 保存临时音频文件到服务器
            with open(temp_file_path, "wb") as f:
                f.write(audio_content)
            
            # 返回文件 ID 
            return {
                "audio_id": file_id,
                "tts": tts
            }
            
    except httpx.RequestError as exc:
        logging.error(f"Request error: {exc}")
        raise HTTPException(status_code=500, detail=f"Request error: {exc}")
    except httpx.HTTPStatusError as exc:
        logging.error(f"HTTP error: {exc}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc}")
    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

@router.get("/previewAudio", summary="预览音频")
async def preview_audio(audio_id: str):
    temp_file_path = os.path.join(temp_audio_save_path, f"{audio_id}.wav")
    
    if not os.path.exists(temp_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(temp_file_path, media_type="audio/wav")

@router.post("/save", summary="保存音频")
async def save_audio(
    audio_in: AudioFileCreate
):
    try:
        temp_file_name = f"{audio_in.audio_id}.wav"
        temp_file_path = os.path.join(temp_audio_save_path, temp_file_name)
        
        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=404, detail="Temporary audio file not found")
        
        # 将临时文件移动到正式存储路径
        final_file_path = os.path.join(final_audio_save_path, temp_file_name)
        os.rename(temp_file_path, final_file_path)
        
        audioin = {
            "user_id": audio_in.user_id,
            "tone_name": "",
            "file_name": temp_file_name,
            "file_path": final_file_path,
            "text_info": audio_in.text_info,
            "cloned_voice": False,
            "build_in": audio_in.build_in,
            "tone_avatar": ""
        }
        # 保存音频文件的信息到数据库
        await audio_controller.save_audio_to_db(audioin) 
        return Success(msg="Audio saved successfully", file_path=final_file_path)
        
    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

@router.delete("/delete",summary="删除音频")
async def delete_audio(id: int = Query(..., description="音频ID")):
    await audio_controller.delete_audio(id=id)
    return Success(msg="Audio delete successfully")
    
@router.post("/generate_zeroshot",summary="zeroshot获取音频")
async def zero_shot_inference(
    tts: str = Form(...), 
    tone_name: str = Form(...)
    ):
    # 通过audio_file_name获取到 音频数据
    audio = await audio_controller.get_audio_file_by_name(tone_name)
    # url = f"https://{settings.SERVER_IP_COSY}/api/inference/zero-shot"
    url = "/api/inference/zero-shot"
    # 读取上传的音频文件并转换为合适的格式
    prompt = await audio_controller.get_prompt_by_name(tone_name)
    try:
        files = {"audio": ("audio.wav", audio, "audio/wav")}
        data = {"tts": tts, "prompt": prompt}
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            audio_content = response.content
        # 生成唯一的文件名
        file_id = str(uuid.uuid4())
        temp_file_name = f"{file_id}.wav"
        temp_file_path = os.path.join(temp_audio_save_path, temp_file_name)
        
        # 保存临时音频文件到服务器
        with open(temp_file_path, "wb") as f:
            f.write(audio_content)
        
        # 返回文件 ID 
        return {
            "audio_id": file_id,
            "tts": tts,
            "prompt":prompt
        }   
    except httpx.RequestError as exc:
        logging.error(f"Request error: {exc}")
        raise HTTPException(status_code=500, detail=f"Request error: {exc}")
    except httpx.HTTPStatusError as exc:
        logging.error(f"HTTP error: {exc}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"HTTP error: {exc}")
    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")