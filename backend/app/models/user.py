# app/models/user.py
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.models.base import BaseModel
from app.db.database import Base

class User(Base, BaseModel):
    """User model for authentication and authorization."""
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(
        Enum('super_admin', 'admin', 'user_pro', 'user_starter', name='user_roles'), 
        default='user_starter',
        nullable=False
    )
    is_active = Column(Boolean, default=False, nullable=False)
    approval_status = Column(
        Enum('pending', 'approved', 'rejected', name='approval_statuses'), 
        default='pending',
        nullable=False
    )
    
    # Relationships will be added later when other models are defined
