# app/models/rag_system.py
from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

# Association table for many-to-many relationship
rag_documents = Table(
    "rag_documents",
    Base.metadata,
    Column("rag_system_id", String, ForeignKey("rag_systems.id")),
    Column("document_id", String, ForeignKey("documents.id"))
)

class RAGSystem(Base, BaseModel):
    __tablename__ = "rag_systems"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding_model = Column(String, nullable=False)
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="rag_systems")
    documents = relationship("Document", secondary=rag_documents)
