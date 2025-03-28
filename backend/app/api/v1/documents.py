from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, Document, DocumentList
from app.services.document_service import (
    get_documents, get_document_by_id, create_document, 
    upload_document, update_document, delete_document, extract_text
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.get("", response_model=DocumentList)
async def list_all_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user with filtering and pagination."""
    documents, total = await get_documents(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        file_type=file_type
    )
    return {"items": documents, "total": total}

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = get_document_by_id(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("", response_model=Document, status_code=201)
async def create_new_document(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new document directly."""
    return create_document(db, document_in, current_user.id)

@router.post("/upload", response_model=Document, status_code=201)
async def upload_new_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and create a new document from a file."""
    return await upload_document(db, file, title, current_user.id)

@router.post("/{document_id}/extract")
async def extract_document_text(
    document_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Extract text from a document."""
    document = get_document_by_id(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text = await extract_text(document)
    return {"text": text, "document_id": document_id}

@router.put("/{document_id}", response_model=Document)
async def update_existing_document(
    document_id: str = Path(...),
    document_in: DocumentUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing document (metadata only)."""
    document = get_document_by_id(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return update_document(db, document, document_in)

@router.delete("/{document_id}", status_code=204)
async def delete_existing_document(
    document_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = get_document_by_id(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    delete_document(db, document_id)
    return None
