import logging
import uuid

from fastapi import APIRouter, Body, HTTPException, Query,Form,UploadFile, File
from fastapi.responses import FileResponse,JSONResponse
import httpx
from tortoise.expressions import Q

from app.controllers.audio import audio_controller
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.audio import *
from dotenv import load_dotenv
import os

load_dotenv() 
logger = logging.getLogger(__name__)
tone_audio_save_path = os.getenv('TONE_AUDIO_SAVE_PATH')
if not os.path.exists(tone_audio_save_path):
    os.makedirs(tone_audio_save_path)
    
tone_avatar_save_path = os.getenv('TONE_AVATAR_SAVE_PATH')
if not os.path.exists(tone_avatar_save_path):
    os.makedirs(tone_avatar_save_path)
    
router = APIRouter()

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid

router = APIRouter()

@router.post("/create_tone", summary="生成音色")
async def create_tone(
    tone_name: str = Form(example="不能重复"),
    user_id: int = Form(...),
    text_info: str = Form(...),
    cloned_voice: bool = Form(default=True),
    build_in: bool = Form(default=False),
    tag_names: List[str] = Body(default=[]),
    audio_file: UploadFile = File(...),
    avatar_file: UploadFile = File(...),
):
    try:
        # 检查文件类型
        if audio_file.content_type not in ["audio/mpeg", "audio/wav"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
       # 获取文件扩展名
        file_extension = avatar_file.filename.split(".")[-1]
        
        # 生成一个新的文件名，以避免文件名冲突
        unique_id = uuid.uuid4()
        new_filename = f"{unique_id}.{file_extension}"
        
        # 构建完整的文件路径
        avatar_file_path = os.path.join(tone_avatar_save_path, new_filename)
        
        # 读取上传的音频文件内容
        file_content = await audio_file.read()
        
        # 生成唯一的文件名
        file_id = str(uuid.uuid4())
        file_extension = "mp3" if audio_file.content_type == "audio/mpeg" else "wav"
        temp_file_name = f"{file_id}.{file_extension}"
        temp_file_path = os.path.join(tone_audio_save_path, temp_file_name)
        
        # 保存头像文件
        with open(avatar_file_path, "wb") as buffer:
            content = await avatar_file.read()
            buffer.write(content)
        # 保存音色文件到服务器
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        # 创建 ToneFileCreate 实例
        audio_in = {
            "user_id": user_id,
            "tone_name": tone_name,
            "file_name": temp_file_name,
            "file_path": tone_audio_save_path,
            "text_info": text_info,
            "cloned_voice": cloned_voice,
            "build_in": build_in,
            "tone_avatar": new_filename
        }
        
        # 保存到数据库
        audio_file_new = await audio_controller.save_audio_to_db(audio_in)
        
        # 添加标签
        await audio_controller.add_tags_to_audio_file(audio_file_new.id, tag_names)
        
        return JSONResponse(content={"message": "音色创建成功", "filename": temp_file_name})
    except Exception as e:
        return JSONResponse(content={"message": "音色创建失败", "error": str(e)}, status_code=500)

@router.delete("/delete",summary="删除音色")
async def delete_tone(id: int = Query(..., description="音色ID")):
    await audio_controller.delete_tone(id=id)
    return Success(msg="Tone delete successfully")

@router.get("/tone_list",summary="获取音色列表")
async def tone_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    user_id: int= Query(1, description="用户id"),
    cloned_voice: bool = Query(True,description="是否是音色")
):
    q = Q()
    if user_id:
        q &= Q(user_id=user_id)
    if cloned_voice is not None:
        q &= Q(cloned_voice=cloned_voice)
    total, user_objs = await audio_controller.list(page=page, page_size=page_size, search=q)
    data = [await obj.to_dict(m2m=True) for obj in user_objs]

    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)
