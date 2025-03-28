from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Any
from uuid import uuid4

from app.models.rag_system import RAGSystem
from app.models.document import Document
from app.models.embedding import Embedding
from app.models.vector_db import VectorDB
from app.schemas.rag_system import RAGSystemCreate, RAGSystemUpdate

def get_rag_systems(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> Tuple[List[RAGSystem], int]:
    """Get RAG systems with pagination."""
    query = db.query(RAGSystem).filter(RAGSystem.creator_id == user_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    rag_systems = query.order_by(RAGSystem.updated_at.desc()).offset(skip).limit(limit).all()
    
    return rag_systems, total

def get_rag_system_by_id(db: Session, rag_system_id: str, user_id: str) -> Optional[RAGSystem]:
    """Get a RAG system by ID with user check."""
    rag_system = db.query(RAGSystem).filter(RAGSystem.id == rag_system_id).first()
    
    # Check if RAG system exists and belongs to user
    if rag_system is None or rag_system.creator_id != user_id:
        return None
    
    return rag_system

def create_rag_system(db: Session, rag_system_in: RAGSystemCreate, user_id: str) -> RAGSystem:
    """Create a new RAG system."""
    # Verify all documents exist and belong to user
    for doc_id in rag_system_in.documents:
        document = db.query(Document).filter(
            Document.id == doc_id,
            Document.creator_id == user_id
        ).first()
        
        if document is None:
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
    
    # Create RAG system
    db_rag_system = RAGSystem(
        id=str(uuid4()),
        name=rag_system_in.name,
        description=rag_system_in.description,
        embedding_model=rag_system_in.embedding_model,
        documents=rag_system_in.documents,
        creator_id=user_id
    )
    
    db.add(db_rag_system)
    db.commit()
    db.refresh(db_rag_system)
    
    return db_rag_system

def update_rag_system(db: Session, rag_system: RAGSystem, rag_system_in: RAGSystemUpdate) -> RAGSystem:
    """Update a RAG system."""
    update_data = rag_system_in.dict(exclude_unset=True)
    
    # If documents are being updated, verify they exist and belong to user
    if "documents" in update_data:
        for doc_id in update_data["documents"]:
            document = db.query(Document).filter(
                Document.id == doc_id,
                Document.creator_id == rag_system.creator_id
            ).first()
            
            if document is None:
                raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
    
    # Update RAG system attributes
    for key, value in update_data.items():
        setattr(rag_system, key, value)
    
    db.add(rag_system)
    db.commit()
    db.refresh(rag_system)
    
    return rag_system

def delete_rag_system(db: Session, rag_system_id: str) -> None:
    """Delete a RAG system."""
    rag_system = db.query(RAGSystem).filter(RAGSystem.id == rag_system_id).first()
    if rag_system is None:
        raise HTTPException(status_code=404, detail="RAG system not found")
    
    db.delete(rag_system)
    db.commit()

async def test_rag_system(db: Session, rag_system: RAGSystem, query_text: str) -> Dict[str, Any]:
    """Test a RAG system with a query.
    
    In a real application, this would:
    1. Get embeddings for documents
    2. Create an embedding for the query
    3. Find relevant chunks using vector similarity
    4. Construct a prompt with context
    5. Generate a response using an LLM
    
    For now, we'll return a mock response.
    """
    # Get documents associated with the RAG system
    document_ids = rag_system.documents
    
    # Mock retrieval and generation
    return {
        "query": query_text,
        "retrieved_chunks": [
            {"text": f"Retrieved chunk from document {doc_id}", "score": round(0.7 + 0.2 * random.random(), 3)}
            for doc_id in document_ids[:3]  # Use up to 3 documents for demonstration
        ],
        "response": f"This is a generated response based on the retrieved context about: {query_text}",
        "model_used": "llama3",
        "embedding_model": rag_system.embedding_model
    }
