from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.prompt import PromptCreate, PromptUpdate, Prompt, PromptList
from app.services.prompt_service import (
    get_prompts, get_prompt_by_id, create_prompt, 
    update_prompt, delete_prompt
)

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])

@router.get("", response_model=PromptList)
async def list_all_prompts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all prompts for the current user with filtering and pagination."""
    prompts, total = await get_prompts(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        category=category,
        tag=tag
    )
    return {"items": prompts, "total": total}

@router.get("/{prompt_id}", response_model=Prompt)
async def get_prompt(
    prompt_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific prompt by ID."""
    prompt = await get_prompt_by_id(db, prompt_id, current_user.id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.post("", response_model=Prompt, status_code=201)
async def create_new_prompt(
    prompt_in: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new prompt."""
    return await create_prompt(db, prompt_in, current_user.id)

@router.put("/{prompt_id}", response_model=Prompt)
async def update_existing_prompt(
    prompt_id: str = Path(...),
    prompt_in: PromptUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing prompt."""
    prompt = await get_prompt_by_id(db, prompt_id, current_user.id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return await update_prompt(db, prompt, prompt_in)

@router.delete("/{prompt_id}", status_code=204)
async def delete_existing_prompt(
    prompt_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a prompt."""
    prompt = await get_prompt_by_id(db, prompt_id, current_user.id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    await delete_prompt(db, prompt_id)
    return None
