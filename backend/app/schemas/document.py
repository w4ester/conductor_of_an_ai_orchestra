from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    file_type: str

class DocumentCreate(DocumentBase):
    content: str  # Base64-encoded content

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    
class DocumentInDB(DocumentBase):
    id: str
    content: str  # Base64-encoded content
    creator_id: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class Document(DocumentInDB):
    pass

class DocumentList(BaseModel):
    items: List[Document]
    total: int
