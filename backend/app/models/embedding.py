# app/models/embedding.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, JSON, Index
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from app.db.database import Base
from app.models.base import BaseModel

class Embedding(Base, BaseModel):
    __tablename__ = "embeddings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    vector_db_id = Column(String, ForeignKey("vector_dbs.id", ondelete="CASCADE"), nullable=False)
    model = Column(String, nullable=False)
    dimensions = Column(Integer, nullable=False)
    creator_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chunks = Column(Text, nullable=True)  # JSON string of chunks
    status = Column(String, nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    error = Column(Text, nullable=True)  # Error message if status is failed
    chunk_size = Column(Integer, nullable=True)
    chunk_overlap = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    vector_db = relationship("VectorDB", back_populates="embeddings")
    creator = relationship("User", back_populates="embeddings")
    
    # Additional indices
    __table_args__ = (
        Index("ix_embeddings_document_id", "document_id"),
        Index("ix_embeddings_vector_db_id", "vector_db_id"),
        Index("ix_embeddings_creator_id", "creator_id"),
        Index("ix_embeddings_model", "model"),
        Index("ix_embeddings_status", "status"),
    )
