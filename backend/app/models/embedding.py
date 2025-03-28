# app/models/embedding.py
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class Embedding(Base, BaseModel):
    __tablename__ = "embeddings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    model = Column(String, nullable=False)
    dimensions = Column(Integer, nullable=False)
    chunks = Column(JSON, nullable=True)
    
    # Foreign keys
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    vector_db_id = Column(String, ForeignKey("vector_databases.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    vector_db = relationship("VectorDatabase", back_populates="embeddings")
    creator = relationship("User")
