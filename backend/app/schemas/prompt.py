from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class PromptBase(BaseModel):
    title: str
    content: str
    model: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class PromptInDB(PromptBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Prompt(PromptInDB):
    pass

class PromptList(BaseModel):
    items: List[Prompt]
    total: int
