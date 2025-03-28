from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Any
from uuid import uuid4
import random
import json
from datetime import datetime

from app.models.embedding import Embedding
from app.models.document import Document
from app.models.vector_db import VectorDB
from app.schemas.embedding import EmbeddingCreate
from app.core.cache import cached, cache_delete_pattern, cache_set, cache_get
from app.core.background import run_in_background, get_task_info, TaskStatus

async def get_embeddings(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    document_id: Optional[str] = None,
    vector_db_id: Optional[str] = None
) -> Tuple[List[Embedding], int]:
    """Get embeddings with filtering and pagination."""
    cache_key = f"embeddings_{user_id}_{skip}_{limit}_{document_id}_{vector_db_id}"
    cached_result = await cache_get(cache_key)
    
    if cached_result:
        return cached_result
    
    query = db.query(Embedding).filter(Embedding.creator_id == user_id)
    
    # Apply filters
    if document_id:
        query = query.filter(Embedding.document_id == document_id)
    
    if vector_db_id:
        query = query.filter(Embedding.vector_db_id == vector_db_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination with optimized query
    embeddings = query.order_by(Embedding.created_at.desc()).offset(skip).limit(limit).all()
    
    result = (embeddings, total)
    await cache_set(cache_key, result)
    
    return result

async def get_embedding_by_id(db: Session, embedding_id: str, user_id: str) -> Optional[Embedding]:
    """Get an embedding by ID with user check."""
    cache_key = f"embedding_{embedding_id}_{user_id}"
    cached_embedding = await cache_get(cache_key)
    
    if cached_embedding:
        return cached_embedding
    
    embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    
    # Check if embedding exists and belongs to user
    if embedding is None or embedding.creator_id != user_id:
        return None
    
    await cache_set(cache_key, embedding)
    return embedding

async def create_embedding(db: Session, embedding_in: EmbeddingCreate, user_id: str) -> Dict[str, Any]:
    """
    Start embedding creation as a background task.
    Returns task_id that can be used to check on progress.
    """
    # Verify document exists and belongs to user
    document = db.query(Document).filter(
        Document.id == embedding_in.document_id,
        Document.creator_id == user_id
    ).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify vector database exists and belongs to user
    vector_db = db.query(VectorDB).filter(
        VectorDB.id == embedding_in.vector_db_id,
        VectorDB.creator_id == user_id
    ).first()
    
    if vector_db is None:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    # Create a placeholder embedding record
    embedding_id = str(uuid4())
    db_embedding = Embedding(
        id=embedding_id,
        document_id=embedding_in.document_id,
        vector_db_id=embedding_in.vector_db_id,
        model=embedding_in.model,
        dimensions=determine_model_dimensions(embedding_in.model),
        creator_id=user_id,
        status="pending",
        chunk_size=embedding_in.chunk_size,
        chunk_overlap=embedding_in.chunk_overlap
    )
    
    db.add(db_embedding)
    db.commit()
    
    # Start background task
    task_id = await run_in_background(
        _process_embedding,
        db_session_factory=db.bind.pool._creator,
        embedding_id=embedding_id,
        document_id=embedding_in.document_id,
        chunk_size=embedding_in.chunk_size,
        chunk_overlap=embedding_in.chunk_overlap,
        model=embedding_in.model
    )
    
    # Return task ID and embedding ID
    return {
        "task_id": task_id,
        "embedding_id": embedding_id,
        "status": "processing"
    }

async def check_embedding_status(task_id: str) -> Dict[str, Any]:
    """Check the status of an embedding task."""
    task_info = get_task_info(task_id)
    return task_info

async def get_embedding_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of an embedding task by its task ID."""
    return await check_embedding_status(task_id)

async def _process_embedding(
    db_session_factory,
    embedding_id: str,
    document_id: str,
    chunk_size: int,
    chunk_overlap: int,
    model: str
) -> Dict[str, Any]:
    """
    Process document embedding in the background.
    This function runs in a separate task.
    """
    # Create a new database session for this background task
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_session_factory())
    db = SessionLocal()
    
    try:
        # Get the embedding record
        embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
        if not embedding:
            raise Exception(f"Embedding {embedding_id} not found")
        
        # Update status
        embedding.status = "processing"
        db.commit()
        
        # Get the document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise Exception(f"Document {document_id} not found")
        
        # Extract text from document
        from app.services.document_service import extract_text
        text = await extract_text(document)
        
        # Create chunks
        chunks = create_chunks(text, chunk_size, chunk_overlap)
        
        # In a real application, we would create actual embeddings here
        # For now, we'll just save the chunks
        embedding.chunks = json.dumps(chunks)
        embedding.status = "completed"
        embedding.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Invalidate cache
        await cache_delete_pattern(f"embedding_{embedding_id}*")
        await cache_delete_pattern(f"embeddings_{embedding.creator_id}*")
        
        return {
            "embedding_id": embedding_id,
            "status": "completed",
            "num_chunks": len(chunks)
        }
    except Exception as e:
        # Update status to failed
        if embedding:
            embedding.status = "failed"
            embedding.error = str(e)
            db.commit()
        
        raise
    finally:
        db.close()

async def delete_embedding(db: Session, embedding_id: str) -> None:
    """Delete an embedding."""
    embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    user_id = embedding.creator_id
    
    db.delete(embedding)
    db.commit()
    
    # Invalidate cache
    await cache_delete_pattern(f"embedding_{embedding_id}*")
    await cache_delete_pattern(f"embeddings_{user_id}*")

def create_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
    """Create text chunks from a document.
    
    In a real application, this would implement a proper chunking algorithm.
    For now, we'll create mock chunks.
    """
    # Simple chunking algorithm
    chunks = []
    
    # If text is shorter than chunk size, just return one chunk
    if len(text) <= chunk_size:
        chunks.append({
            "text": text,
            "metadata": {
                "start": 0,
                "end": len(text),
                "position": 0
            }
        })
        return chunks
    
    # Split into overlapping chunks
    for i in range(0, len(text), chunk_size - chunk_overlap):
        end = min(i + chunk_size, len(text))
        if i >= len(text):
            break
            
        chunk_text = text[i:end]
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "start": i,
                "end": end,
                "position": len(chunks)
            }
        })
        
        # If we've reached the end, stop
        if end == len(text):
            break
    
    return chunks

def determine_model_dimensions(model_name: str) -> int:
    """Determine embedding dimensions based on model name."""
    # Common embedding dimensions
    if "large" in model_name.lower():
        return 1024
    elif "small" in model_name.lower():
        return 384
    else:
        # Default for medium/base models
        return 768

def get_embedding_models() -> List[Dict[str, Any]]:
    """Get list of supported embedding models."""
    # In a real application, we would get this from Ollama or another source
    return [
        {"name": "nomic-embed-text", "dimensions": 768, "description": "General purpose text embedding model"},
        {"name": "all-minilm-l6-v2", "dimensions": 384, "description": "Fast, efficient embedding model"},
        {"name": "e5-small-v2", "dimensions": 384, "description": "Small, efficient text embedding model"},
        {"name": "e5-large-v2", "dimensions": 1024, "description": "Large, high-quality text embedding model"},
        {"name": "bge-small-en", "dimensions": 384, "description": "BGE small model for English text"},
        {"name": "bge-large-en", "dimensions": 1024, "description": "BGE large model for English text"}
    ]
