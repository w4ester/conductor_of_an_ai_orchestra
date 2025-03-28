from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.vector_db import VectorDBCreate, VectorDBUpdate, VectorDB, VectorDBList
from app.services.vector_db_service import (
    get_vector_dbs, get_vector_db_by_id, create_vector_db, 
    delete_vector_db, get_vector_db_types
)

router = APIRouter(prefix="/api/v1/vector-dbs", tags=["vector databases"])

@router.get("", response_model=VectorDBList)
async def list_all_vector_dbs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all vector databases for the current user with filtering and pagination."""
    vector_dbs, total = get_vector_dbs(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        db_type=db_type
    )
    return {"items": vector_dbs, "total": total}

@router.get("/collections", response_model=List[Dict])
async def get_collections_for_chat(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all collections that can be used for RAG in chat."""
    dbs, _ = get_vector_dbs(db, user_id=current_user.id, limit=100)
    
    # Convert to the format expected by the frontend
    result = [
        {
            "id": db.id,
            "name": db.name,
            "type": db.type,
            "document_count": 0  # In a real implementation, you would query the actual count
        }
        for db in dbs
    ]
    
    return result

@router.get("/types", response_model=List[Dict[str, str]])
async def list_vector_db_types(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of supported vector database types."""
    return get_vector_db_types()

@router.get("/{db_id}", response_model=VectorDB)
async def get_vector_db(
    db_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific vector database by ID."""
    vector_db = get_vector_db_by_id(db, db_id, current_user.id)
    if vector_db is None:
        raise HTTPException(status_code=404, detail="Vector database not found")
    return vector_db

@router.post("", response_model=VectorDB, status_code=201)
async def create_new_vector_db(
    vector_db_in: VectorDBCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new vector database configuration."""
    return create_vector_db(db, vector_db_in, current_user.id)

@router.delete("/{db_id}", status_code=204)
async def delete_existing_vector_db(
    db_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a vector database configuration."""
    vector_db = get_vector_db_by_id(db, db_id, current_user.id)
    if vector_db is None:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    delete_vector_db(db, db_id)
    return None
