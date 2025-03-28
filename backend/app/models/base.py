# app/models/base.py
from sqlalchemy import Column, DateTime, func, Index
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class BaseModel:
    """Base class for all models with common columns and methods."""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, index=True)
    
    @declared_attr
    def __table_args__(cls):
        return (
            # Add index on created_at and updated_at
            Index(f'ix_{cls.__tablename__}_created_at', 'created_at'),
            Index(f'ix_{cls.__tablename__}_updated_at', 'updated_at'),
        )
