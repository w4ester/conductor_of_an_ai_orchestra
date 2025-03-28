from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any, Tuple

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.embedding import Embedding
from app.schemas.embedding import (
    EmbeddingCreate, Embedding as EmbeddingSchema, 
    EmbeddingList, EmbeddingTaskResponse
)
from app.services.embedding_service import (
    get_embeddings, get_embedding_by_id, 
    create_embedding, delete_embedding,
    get_embedding_task_status
)

router = APIRouter(prefix="/api/v1/embeddings", tags=["embeddings"])

@router.get("", response_model=EmbeddingList)
async def list_embeddings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    document_id: Optional[str] = None,
    vector_db_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all embeddings with filtering and pagination."""
    embeddings, total = get_embeddings(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        document_id=document_id,
        vector_db_id=vector_db_id
    )
    return {"items": embeddings, "total": total}

@router.get("/models", response_model=List[Dict])
async def get_embedding_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get available embedding models."""
    # Return default and local embedding models based on user's request
    return [
        {
            "name": "all-minilm:22m",
            "dimensions": 384,
            "description": "Local all-MiniLM-L6-v2 embedding model (22M parameters)"
        },
        {
            "name": "nomic-embed-text:latest",
            "dimensions": 768,
            "description": "Local Nomic AI embedding model"
        },
        {
            "name": "text-embedding-3-small",
            "dimensions": 1536,
            "description": "OpenAI text-embedding-3-small model (free tier)"
        },
        {
            "name": "text-embedding-3-large",
            "dimensions": 3072,
            "description": "OpenAI text-embedding-3-large model (paid)"
        },
        {
            "name": "snowflake-arctic-embed2",
            "dimensions": 1024,
            "description": "Snowflake Arctic Embed2 model"
        }
    ]

@router.get("/{embedding_id}", response_model=EmbeddingSchema)
async def get_embedding(
    embedding_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific embedding by ID."""
    embedding = get_embedding_by_id(db, embedding_id, current_user.id)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embedding

@router.post("", response_model=EmbeddingTaskResponse)
async def create_embedding_task(
    embedding_request: EmbeddingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create an embedding (starts async task)."""
    return create_embedding(db, embedding_request, current_user.id)

@router.get("/tasks/{task_id}")
async def check_task_status(
    task_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check embedding task status."""
    return get_embedding_task_status(task_id)

@router.delete("/{embedding_id}", status_code=204)
async def delete_existing_embedding(
    embedding_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an embedding."""
    embedding = get_embedding_by_id(db, embedding_id, current_user.id)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    delete_embedding(db, embedding_id)
    return None
