from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import json

from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate
from app.core.cache import cached, cache_delete_pattern, cache_set, cache_get

async def get_prompts(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    tag: Optional[str] = None
) -> Tuple[List[Prompt], int]:
    """Get prompts with filtering and pagination."""
    cache_key = f"prompts_{user_id}_{skip}_{limit}_{category}_{tag}"
    cached_result = await cache_get(cache_key)
    
    if cached_result:
        return cached_result
    
    query = db.query(Prompt).filter(Prompt.creator_id == user_id)
    
    # Apply filters
    if category:
        query = query.filter(Prompt.category == category)
    
    if tag:
        # Use more efficient LIKE query for JSON tags
        # This assumes tags are stored as a JSON array string
        query = query.filter(text(f"tags LIKE '%{tag}%'"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination with optimized query
    prompts = query.order_by(Prompt.updated_at.desc()).offset(skip).limit(limit).all()
    
    result = (prompts, total)
    await cache_set(cache_key, result)
    
    return result

async def get_prompt_by_id(db: Session, prompt_id: str, user_id: str) -> Optional[Prompt]:
    """Get a prompt by ID with user check."""
    cache_key = f"prompt_{prompt_id}_{user_id}"
    cached_prompt = await cache_get(cache_key)
    
    if cached_prompt:
        return cached_prompt
    
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    
    # Check if prompt exists and belongs to user
    if prompt is None or prompt.creator_id != user_id:
        return None
    
    await cache_set(cache_key, prompt)
    return prompt

async def create_prompt(db: Session, prompt_in: PromptCreate, user_id: str) -> Prompt:
    """Create a new prompt."""
    # Convert tags to JSON if provided
    tags_json = json.dumps(prompt_in.tags) if prompt_in.tags else None
    
    # Create prompt
    db_prompt = Prompt(
        id=str(uuid4()),
        title=prompt_in.title,
        content=prompt_in.content,
        model=prompt_in.model,
        category=prompt_in.category,
        tags=tags_json,
        creator_id=user_id
    )
    
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    
    # Invalidate cache for this user's prompts
    await cache_delete_pattern(f"prompts_{user_id}*")
    
    return db_prompt

async def update_prompt(db: Session, prompt: Prompt, prompt_in: PromptUpdate) -> Prompt:
    """Update a prompt."""
    update_data = prompt_in.dict(exclude_unset=True)
    
    # Convert tags to JSON if provided
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"])
    
    # Update prompt attributes
    for key, value in update_data.items():
        setattr(prompt, key, value)
    
    # Update timestamp
    prompt.updated_at = datetime.utcnow()
    
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    
    # Invalidate cache
    await cache_delete_pattern(f"prompts_{prompt.creator_id}*")
    await cache_delete_pattern(f"prompt_{prompt.id}*")
    
    return prompt

async def delete_prompt(db: Session, prompt_id: str) -> None:
    """Delete a prompt."""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    user_id = prompt.creator_id
    
    db.delete(prompt)
    db.commit()
    
    # Invalidate cache
    await cache_delete_pattern(f"prompts_{user_id}*")
    await cache_delete_pattern(f"prompt_{prompt_id}*")
