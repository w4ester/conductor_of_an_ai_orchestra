from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ToolBase(BaseModel):
    name: str
    description: str
    code: str
    language: str = "python"

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None

class ToolInDB(ToolBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class Tool(ToolInDB):
    pass

class ToolList(BaseModel):
    items: List[Tool]
    total: int
