# app/models/vector_db.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class VectorDB(Base, BaseModel):
    __tablename__ = "vector_dbs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "chroma", "pinecone", etc.
    connection_string = Column(String, nullable=True)
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    embeddings = relationship("Embedding", back_populates="vector_db", cascade="all, delete-orphan")
