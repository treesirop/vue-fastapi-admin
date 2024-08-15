from pydantic import BaseModel, Field
from typing import Optional

class BaseTag(BaseModel):
    id: int
    tag_name: str

class TagCreate(BaseModel):
    tag_name: str = Field(example="Example Tag")

class TagUpdate(BaseModel):
    id: int = Field(example=1)
    tag_name: Optional[str] = Field(None, example="Updated Tag Name")
