from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class VectorDBBase(BaseModel):
    name: str
    type: str
    connection_string: Optional[str] = None

class VectorDBCreate(VectorDBBase):
    pass

class VectorDBUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    connection_string: Optional[str] = None

class VectorDBInDB(VectorDBBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class VectorDB(VectorDBInDB):
    pass

class VectorDBList(BaseModel):
    items: List[VectorDB]
    total: int
