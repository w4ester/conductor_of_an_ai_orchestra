"""
This module sets up default vector database collections for new installations.
"""
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from datetime import datetime

from app.models.vector_db import VectorDatabase
from app.models.user import User

def create_sample_collections(db: Session, admin_user_id: str) -> List[VectorDatabase]:
    """Create sample vector database collections for new installations."""
    
    # Check if collections already exist
    existing_collections = db.query(VectorDatabase).count()
    if existing_collections > 0:
        # Collections already exist, don't create duplicates
        return []
    
    # Create sample collections
    collections = [
        VectorDatabase(
            id=str(uuid4()),
            name="General Knowledge",
            type="chroma",
            connection_string="local:./data/vector_dbs/general",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        VectorDatabase(
            id=str(uuid4()),
            name="Workshop Documentation",
            type="chroma",
            connection_string="local:./data/vector_dbs/workshop",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        VectorDatabase(
            id=str(uuid4()),
            name="Technical Reference",
            type="chroma",
            connection_string="local:./data/vector_dbs/technical",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]
    
    # Add the collections to the database
    for collection in collections:
        db.add(collection)
    
    db.commit()
    
    # Return the created collections
    return collections

def setup_default_collections(db: Session):
    """Set up default vector database collections for new installations."""
    # Find the first admin user (or any user if no admin exists)
    admin = db.query(User).filter(User.is_admin == True).first()
    
    # If no admin exists, use the first user
    if not admin:
        admin = db.query(User).first()
        
    # If no users exist at all, we can't create collections yet
    if not admin:
        print("No users found. Cannot create default collections.")
        return []
    
    # Create sample collections
    return create_sample_collections(db, admin.id)
