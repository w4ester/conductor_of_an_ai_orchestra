from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
import json
from datetime import datetime

class PromptBase(BaseModel):
    title: str
    content: str
    model: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    
    # Add validator for tags to handle string representation
    @validator('tags', pre=True)
    def validate_tags(cls, v):
        # Handle string representation of list
        if isinstance(v, str):
            try:
                # Try to parse as JSON if it's a string
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, treat as a single tag
                return [v]
        return v or []

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Add same validator for update schema
    @validator('tags', pre=True)
    def validate_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return [v]
        return v or []

class PromptInDB(PromptBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    # Add validator to handle tags when retrieving from database
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []
    
    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2
        populate_by_name = True  # Ensures field aliasing works

class Prompt(PromptInDB):
    pass

class PromptList(BaseModel):
    items: List[Prompt]
    total: int
