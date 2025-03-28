# app/models/user.py
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class User(Base, BaseModel):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Relationships will be added as you create the related models
    prompts = relationship("Prompt", back_populates="creator", cascade="all, delete-orphan")
    tools = relationship("Tool", back_populates="creator", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="creator", cascade="all, delete-orphan")
    rag_systems = relationship("RAGSystem", back_populates="creator", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="creator", cascade="all, delete-orphan")
    
    # Property for backward compatibility with is_active
    @property
    def is_active(self):
        return not self.disabled
