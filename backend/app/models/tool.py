# app/models/tool.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class Tool(Base, BaseModel):
    __tablename__ = "tools"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    code = Column(Text, nullable=False)
    language = Column(String, default="python")
    
    # Foreign keys
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="tools")
