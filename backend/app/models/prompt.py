# app/models/prompt.py
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class Prompt(Base, BaseModel):
    __tablename__ = "prompts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    category = Column(String, nullable=True)
    
    # Use JSON for SQLite compatibility
    tags = Column(JSON, nullable=True)  # Store as JSON array
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="prompts")
