"""
This module sets up default prompts for new installations.
"""
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from datetime import datetime

from app.models.prompt import Prompt
from app.models.user import User

def create_sample_prompts(db: Session, admin_user_id: str) -> List[Prompt]:
    """Create sample prompts for new installations."""
    
    # Check if prompts already exist
    existing_prompts = db.query(Prompt).count()
    if existing_prompts > 0:
        # Prompts already exist, don't create duplicates
        return []
    
    # Create sample prompts
    prompts = [
        Prompt(
            id=str(uuid4()),
            title="Default Assistant",
            content="You are a helpful, harmless, and honest AI assistant. Answer the user's questions accurately and be helpful.",
            model="*",
            category="general",
            tags=["default", "assistant"],
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Prompt(
            id=str(uuid4()),
            title="Code Helper",
            content="""You are a helpful programming assistant specialized in writing clean, efficient code. When the user asks for code:
1. Make sure you understand their requirements fully
2. Write code that is well-documented and follows best practices
3. Explain your implementation approach
4. Include example usage when relevant""",
            model="*",
            category="programming",
            tags=["code", "programming"],
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Prompt(
            id=str(uuid4()),
            title="Workshop Assistant",
            content="""You are a specialized AI assistant for the Ollama Workshop. Your purpose is to help attendees understand and work with:
1. Local AI models using Ollama
2. Creating and customizing model prompts
3. Working with tools and embeddings
4. Building RAG applications

Be concise, practical, and focus on helping users accomplish tasks with their local models.""",
            model="*",
            category="workshop",
            tags=["workshop", "ollama", "rag"],
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Prompt(
            id=str(uuid4()),
            title="Data Analyst",
            content="""You are a data analysis expert. Help the user with:
1. Understanding and interpreting their data
2. Suggesting appropriate analysis techniques
3. Explaining statistical concepts
4. Recommending visualizations
5. Drawing insights from results

When providing explanations, balance technical accuracy with clarity.""",
            model="*",
            category="data",
            tags=["data", "analysis", "statistics"],
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]
    
    # Add the prompts to the database
    for prompt in prompts:
        db.add(prompt)
    
    db.commit()
    
    # Return the created prompts
    return prompts

def setup_default_prompts(db: Session):
    """Set up default prompts for new installations."""
    # Find the first admin user (or any user if no admin exists)
    admin = db.query(User).filter(User.is_admin == True).first()
    
    # If no admin exists, use the first user
    if not admin:
        admin = db.query(User).first()
        
    # If no users exist at all, we can't create prompts yet
    if not admin:
        print("No users found. Cannot create default prompts.")
        return []
    
    # Create sample prompts
    return create_sample_prompts(db, admin.id)
