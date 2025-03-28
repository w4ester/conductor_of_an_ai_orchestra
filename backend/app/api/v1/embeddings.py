from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.embedding import EmbeddingCreate, Embedding, EmbeddingList
from app.services.embedding_service import (
    get_embeddings, get_embedding_by_id, create_embedding, 
    delete_embedding, get_embedding_models, check_embedding_status
)

router = APIRouter(prefix="/api/v1/embeddings", tags=["embeddings"])

@router.get("", response_model=EmbeddingList)
async def list_all_embeddings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    document_id: Optional[str] = None,
    vector_db_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all embeddings for the current user with filtering and pagination."""
    embeddings, total = await get_embeddings(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        document_id=document_id,
        vector_db_id=vector_db_id
    )
    return {"items": embeddings, "total": total}

@router.get("/models", response_model=List[Dict[str, Any]])
async def list_embedding_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of supported embedding models."""
    return get_embedding_models()

@router.get("/{embedding_id}", response_model=Embedding)
async def get_embedding(
    embedding_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific embedding by ID."""
    embedding = await get_embedding_by_id(db, embedding_id, current_user.id)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embedding

@router.post("", status_code=202)
async def create_new_embedding(
    embedding_in: EmbeddingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start creating a new embedding from a document (async process)."""
    return await create_embedding(db, embedding_in, current_user.id)

@router.get("/tasks/{task_id}")
async def check_task_status(
    task_id: str = Path(...),
    current_user: User = Depends(get_current_active_user)
):
    """Check the status of an embedding task."""
    return await check_embedding_status(task_id)

@router.delete("/{embedding_id}", status_code=204)
async def delete_existing_embedding(
    embedding_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an embedding."""
    embedding = await get_embedding_by_id(db, embedding_id, current_user.id)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    await delete_embedding(db, embedding_id)
    return None
