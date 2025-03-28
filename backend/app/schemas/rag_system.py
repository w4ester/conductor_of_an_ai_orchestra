from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class RAGSystemBase(BaseModel):
    name: str
    description: str
    embedding_model: str
    documents: List[str]  # List of document IDs

class RAGSystemCreate(RAGSystemBase):
    pass

class RAGSystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    embedding_model: Optional[str] = None
    documents: Optional[List[str]] = None

class RAGSystemInDB(RAGSystemBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class RAGSystem(RAGSystemInDB):
    pass

class RAGSystemList(BaseModel):
    items: List[RAGSystem]
    total: int

class RAGSystemQuery(BaseModel):
    text: str
