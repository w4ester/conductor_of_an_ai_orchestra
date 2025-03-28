from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class EmbeddingBase(BaseModel):
    document_id: str
    vector_db_id: str
    model: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

class EmbeddingCreate(EmbeddingBase):
    pass

class EmbeddingUpdate(BaseModel):
    model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None

class EmbeddingInDB(EmbeddingBase):
    id: str
    dimensions: int
    creator_id: str
    status: str
    error: Optional[str] = None
    chunks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class Embedding(EmbeddingInDB):
    pass

class EmbeddingList(BaseModel):
    items: List[Embedding]
    total: int

class EmbeddingTaskResponse(BaseModel):
    task_id: str
    embedding_id: str
    status: str
