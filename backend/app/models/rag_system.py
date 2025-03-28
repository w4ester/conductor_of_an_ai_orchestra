# app/models/rag_system.py
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class RAGSystem(Base, BaseModel):
    __tablename__ = "rag_systems"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    embedding_model = Column(String, nullable=False)
    
    # Use JSON for SQLite compatibility
    documents = Column(JSON, nullable=False)  # List of document IDs
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="rag_systems")
