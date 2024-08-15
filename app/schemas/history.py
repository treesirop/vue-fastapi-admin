from pydantic import BaseModel, Field
from datetime import datetime

class BaseHistory(BaseModel):
    id: int
    user_id: int
    tts_id: int
    created_at: datetime

class HistoryCreate(BaseModel):
    user_id: int = Field(example=1)
    tts_id: int = Field(example=1)

class HistoryUpdate(BaseModel):
    id: int = Field(example=1)
    user_id: int = Field(example=1)
    tts_id: int = Field(example=1)
