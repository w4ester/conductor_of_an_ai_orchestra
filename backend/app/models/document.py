# app/models/document.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class Document(Base, BaseModel):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Base64-encoded content
    file_type = Column(String, nullable=False)
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="documents")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan")
