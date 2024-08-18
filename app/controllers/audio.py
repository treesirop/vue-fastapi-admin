from typing import List

from fastapi import HTTPException

from app.core.crud import CRUDBase
from app.core.exceptions import DoesNotExistHandle
from app.models.admin import AudioFiles,Tags
from app.schemas.audio import AudioFileCreate, AudioFileFull
import os

class AudioController(CRUDBase[AudioFiles, AudioFileCreate, AudioFileFull]):
    def __init__(self):
        super().__init__(model=AudioFiles)

    async def save_audio_to_db(self, obj_in: AudioFileFull) -> AudioFiles:
        audio_file = await self.create(obj_in)
        return audio_file

    async def delete_audio(self, id: int) -> None:
        try:
            audio = await self.get(id=id)
            if audio.cloned_voice == True:
                raise HTTPException(status_code=500, detail="This is not audio")
            tone_file_path = os.path.join("app/utils/save_audios", audio.file_name)
            await audio.delete()
            if os.path.exists(tone_file_path):
                os.remove(tone_file_path)
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except DoesNotExistHandle:
            raise HTTPException(status_code=404, detail="Audio not found")


    async def delete_tone(self, id: int) -> None:
        try:
            audio = await self.get(id=id)
            tone_file_path = os.path.join("app/utils/tones", audio.file_name)
            await audio.delete()
            if os.path.exists(tone_file_path):
                os.remove(tone_file_path)
            else:
                raise HTTPException(status_code=404, detail="File not found")
            
            avatar_file_path = os.path.join("app/utils/avatars", audio.tone_avatar)
            await audio.delete()
            if os.path.exists(avatar_file_path):
                os.remove(avatar_file_path)
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except DoesNotExistHandle:
            raise HTTPException(status_code=404, detail="Audio not found")
    
    async def get_audio_file_by_name(self, tone_name: str) -> bytes:
        audio_file = await self.model.get(tone_name=tone_name)
        file_path= os.path.join(audio_file.file_path,audio_file.file_name)
        try:
            with open(file_path, "rb") as file:
                audio_content = file.read()
                return audio_content
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    
    async def get_prompt_by_name(self, tone_name: str) -> bytes:
        audio_file = await self.model.get(tone_name=tone_name)
        return audio_file.text_info
    
    async def get_filename_by_name(self, tone_name: str) -> bytes:
        audio_file = await self.model.get(tone_name=tone_name)
        return audio_file.file_name
    
    async def add_tags_to_audio_file(self, audio_file_id: int, tag_names: list):
        audio_file = await self.get(id=audio_file_id)
        for tag_name in tag_names:
            tag, _ = await Tags.get_or_create(tag_name=tag_name)
            await audio_file.tags.add(tag)
            
audio_controller = AudioController()
