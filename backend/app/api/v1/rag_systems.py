from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.rag_system import RAGSystemCreate, RAGSystemUpdate, RAGSystem, RAGSystemList, RAGSystemQuery
from app.services.rag_service import (
    get_rag_systems, get_rag_system_by_id, create_rag_system, 
    update_rag_system, delete_rag_system, test_rag_system
)

router = APIRouter(prefix="/api/v1/rag-systems", tags=["rag systems"])

@router.get("", response_model=RAGSystemList)
async def list_all_rag_systems(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all RAG systems for the current user with pagination."""
    rag_systems, total = get_rag_systems(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    return {"items": rag_systems, "total": total}

@router.get("/{rag_system_id}", response_model=RAGSystem)
async def get_rag_system(
    rag_system_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific RAG system by ID."""
    rag_system = get_rag_system_by_id(db, rag_system_id, current_user.id)
    if rag_system is None:
        raise HTTPException(status_code=404, detail="RAG system not found")
    return rag_system

@router.post("", response_model=RAGSystem, status_code=201)
async def create_new_rag_system(
    rag_system_in: RAGSystemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new RAG system."""
    return create_rag_system(db, rag_system_in, current_user.id)

@router.put("/{rag_system_id}", response_model=RAGSystem)
async def update_existing_rag_system(
    rag_system_id: str = Path(...),
    rag_system_in: RAGSystemUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing RAG system."""
    rag_system = get_rag_system_by_id(db, rag_system_id, current_user.id)
    if rag_system is None:
        raise HTTPException(status_code=404, detail="RAG system not found")
    
    return update_rag_system(db, rag_system, rag_system_in)

@router.delete("/{rag_system_id}", status_code=204)
async def delete_existing_rag_system(
    rag_system_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a RAG system."""
    rag_system = get_rag_system_by_id(db, rag_system_id, current_user.id)
    if rag_system is None:
        raise HTTPException(status_code=404, detail="RAG system not found")
    
    delete_rag_system(db, rag_system_id)
    return None

@router.post("/{rag_system_id}/test")
async def test_existing_rag_system(
    rag_system_id: str = Path(...),
    query: RAGSystemQuery = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test a RAG system with a query."""
    rag_system = get_rag_system_by_id(db, rag_system_id, current_user.id)
    if rag_system is None:
        raise HTTPException(status_code=404, detail="RAG system not found")
    
    return await test_rag_system(db, rag_system, query.text)
