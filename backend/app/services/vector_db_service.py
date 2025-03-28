from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict
from uuid import uuid4

from app.models.vector_db import VectorDB
from app.schemas.vector_db import VectorDBCreate, VectorDBUpdate

def get_vector_dbs(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    db_type: Optional[str] = None
) -> Tuple[List[VectorDB], int]:
    """Get vector databases with filtering and pagination."""
    query = db.query(VectorDB).filter(VectorDB.creator_id == user_id)
    
    # Apply filters
    if db_type:
        query = query.filter(VectorDB.type == db_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    vector_dbs = query.order_by(VectorDB.created_at.desc()).offset(skip).limit(limit).all()
    
    return vector_dbs, total

def get_vector_db_by_id(db: Session, db_id: str, user_id: str) -> Optional[VectorDB]:
    """Get a vector database by ID with user check."""
    vector_db = db.query(VectorDB).filter(VectorDB.id == db_id).first()
    
    # Check if vector DB exists and belongs to user
    if vector_db is None or vector_db.creator_id != user_id:
        return None
    
    return vector_db

def create_vector_db(db: Session, vector_db_in: VectorDBCreate, user_id: str) -> VectorDB:
    """Create a new vector database configuration."""
    # Create vector DB
    db_vector_db = VectorDB(
        id=str(uuid4()),
        name=vector_db_in.name,
        type=vector_db_in.type,
        connection_string=vector_db_in.connection_string,
        creator_id=user_id
    )
    
    db.add(db_vector_db)
    db.commit()
    db.refresh(db_vector_db)
    
    return db_vector_db

def delete_vector_db(db: Session, db_id: str) -> None:
    """Delete a vector database configuration."""
    vector_db = db.query(VectorDB).filter(VectorDB.id == db_id).first()
    if vector_db is None:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    db.delete(vector_db)
    db.commit()

def get_vector_db_types() -> List[Dict[str, str]]:
    """Get list of supported vector database types."""
    # In a real application, we would get this from available integrations
    return [
        {"name": "chroma", "description": "Open-source vector database with simple API"},
        {"name": "pinecone", "description": "Managed vector database service with advanced features"},
        {"name": "qdrant", "description": "Open-source vector search engine"},
        {"name": "weaviate", "description": "Vector database with rich semantic search capabilities"},
        {"name": "milvus", "description": "Open-source vector database for AI applications"},
        {"name": "redis", "description": "In-memory database with vector search capabilities"},
        {"name": "pgvector", "description": "PostgreSQL extension for vector similarity search"}
    ]
