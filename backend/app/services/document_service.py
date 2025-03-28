from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Any
from uuid import uuid4
import base64
from datetime import datetime

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

async def get_documents(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    file_type: Optional[str] = None
) -> Tuple[List[Document], int]:
    """Get documents with filtering and pagination."""
    query = db.query(Document).filter(Document.creator_id == user_id)
    
    # Apply filters
    if file_type:
        query = query.filter(Document.file_type == file_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return documents, total

def get_document_by_id(db: Session, document_id: str, user_id: str) -> Optional[Document]:
    """Get a document by ID with user check."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    # Check if document exists and belongs to user
    if document is None or document.creator_id != user_id:
        return None
    
    return document

def create_document(db: Session, document_in: DocumentCreate, user_id: str) -> Document:
    """Create a new document directly."""
    # Create document
    db_document = Document(
        id=str(uuid4()),
        title=document_in.title,
        content=document_in.content,  # Base64-encoded content
        file_type=document_in.file_type,
        creator_id=user_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

async def upload_document(db: Session, file: UploadFile, title: str, user_id: str) -> Document:
    """Upload and create a new document from a file."""
    # Read file content
    file_content = await file.read()
    
    # Determine file type from extension
    file_extension = file.filename.split('.')[-1].lower()
    
    # Create document
    db_document = Document(
        id=str(uuid4()),
        title=title or file.filename,
        content=base64.b64encode(file_content).decode('utf-8'),  # Base64-encoded content
        file_type=file_extension,
        creator_id=user_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

def update_document(db: Session, document: Document, document_in: DocumentUpdate) -> Document:
    """Update a document (metadata only)."""
    update_data = document_in.dict(exclude_unset=True)
    
    # Update document attributes
    for key, value in update_data.items():
        setattr(document, key, value)
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

def delete_document(db: Session, document_id: str) -> None:
    """Delete a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()

async def extract_text(document: Document) -> str:
    """Extract text from a document.
    
    In a real application, this would use appropriate libraries based on file_type.
    For now, we'll return a mock extraction for most types, or actual text for .txt.
    """
    # Decode the base64 content
    content_bytes = base64.b64decode(document.content)
    
    # Extract text based on file type
    if document.file_type == 'pdf':
        # In a real app, you would use PyPDF2 or similar
        text = f"Extracted text from PDF: {document.title}"
    elif document.file_type == 'docx':
        # In a real app, you would use python-docx or similar
        text = f"Extracted text from Word document: {document.title}"
    elif document.file_type == 'txt':
        # For text files, decode the content directly
        text = content_bytes.decode('utf-8')
    else:
        text = f"Extracted text from {document.file_type.upper()} file: {document.title}"
    
    return text
