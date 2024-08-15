from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class BaseAudioFile(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: str
    text_info: str
    cloned_voice: bool = Field(default=False)
    build_in: bool = Field(default=False)
    created_at: Optional[datetime]
    deleted_at: Optional[datetime]
    tags: Optional[List[int]] = []  # Assuming tags are represented by their IDs

class AudioFileCreate(BaseModel):
    user_id: int = Field(example=1)
    audio_id: str = Field()
    text_info: str = Field(example="Sample text")
    build_in: bool = Field(default=False)

class ToneFileCreate(BaseModel):
    user_id: int = Field(example=1)
    tone_name: str = Field(example="中文女")
    file_name: str = Field(example="example.mp3")
    file_path: str = Field(example="/path/to/file")
    text_info: str = Field(example="Sample text")
    cloned_voice: bool = Field(default=True)
    build_in: bool = Field(default=False)
    tone_avatar: str = Field(example="/path/to/file")
    
class AudioFileFull(BaseModel):
    user_id: int = Field(example=1)
    audio_id: str = Field()
    text_info: str = Field(example="Sample text")
    build_in: bool = Field(default=False)
    file_name: Optional[str] = Field(None, example="example.mp3")
    file_path: Optional[str] = Field(None, example="/path/to/file")
    text_info: Optional[str] = Field(None, example="Updated text")
    cloned_voice: Optional[bool] = Field(default=False)

