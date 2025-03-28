"""
This module sets up default tools for new installations.
"""
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from datetime import datetime

from app.models.tool import Tool
from app.models.user import User

def create_sample_tools(db: Session, admin_user_id: str) -> List[Tool]:
    """Create sample tools for new installations."""
    
    # Check if tools already exist
    existing_tools = db.query(Tool).count()
    if existing_tools > 0:
        # Tools already exist, don't create duplicates
        return []
    
    # Create sample tools
    tools = [
        Tool(
            id=str(uuid4()),
            name="weather_tool",
            description="Get the current weather for a location",
            language="python",
            code="""
def get_weather(location: str):
    # In a real implementation, this would call a weather API
    return {
        "location": location,
        "temperature": 72,
        "condition": "sunny",
        "humidity": 65,
        "wind_speed": 5
    }
""",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Tool(
            id=str(uuid4()),
            name="calculator",
            description="Perform math calculations",
            language="python",
            code="""
def calculate(expression: str):
    # In a real implementation, this would safely evaluate math expressions
    # For now, return a mock result
    return {
        "expression": expression,
        "result": "42",  # Mock result
        "unit": None
    }
""",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Tool(
            id=str(uuid4()),
            name="web_search",
            description="Search the web for information",
            language="python",
            code="""
def search(query: str, num_results: int = 3):
    # In a real implementation, this would call a search API
    return {
        "query": query,
        "results": [
            {
                "title": f"Example result 1 for {query}",
                "url": "https://example.com/1",
                "snippet": f"This is an example search result for {query}..."
            },
            {
                "title": f"Example result 2 for {query}",
                "url": "https://example.com/2",
                "snippet": f"Another example search result for {query}..."
            },
            {
                "title": f"Example result 3 for {query}",
                "url": "https://example.com/3",
                "snippet": f"Yet another example search result for {query}..."
            }
        ][:num_results]
    }
""",
            creator_id=admin_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    # Add the tools to the database
    for tool in tools:
        db.add(tool)
    
    db.commit()
    
    # Return the created tools
    return tools

def setup_default_tools(db: Session):
    """Set up default tools for new installations."""
    # Find the first admin user (or any user if no admin exists)
    admin = db.query(User).filter(User.is_admin == True).first()
    
    # If no admin exists, use the first user
    if not admin:
        admin = db.query(User).first()
        
    # If no users exist at all, we can't create tools yet
    if not admin:
        print("No users found. Cannot create default tools.")
        return []
    
    # Create sample tools
    return create_sample_tools(db, admin.id)
