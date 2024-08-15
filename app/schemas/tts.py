from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseTTSOperation(BaseModel):
    id: int
    user_id: int
    input_text: str
    voice_id: Optional[int] = None
    output_audio_file_id: int
    created_at: datetime
    is_created: bool

class TTSOperationCreate(BaseModel):
    user_id: int = Field(example=1)
    input_text: str = Field(example="Hello world!")
    voice_id: Optional[int] = Field(None, example=1)
    output_audio_file_id: int = Field(example=1)
    is_created: bool = Field(default=False, example=False)

class TTSOperationUpdate(BaseModel):
    id: int = Field(example=1)
    input_text: Optional[str] = Field(None, example="Updated text")
    voice_id: Optional[int] = Field(None, example=1)
    output_audio_file_id: Optional[int] = Field(None, example=1)
    is_created: Optional[bool] = Field(None, example=True)
