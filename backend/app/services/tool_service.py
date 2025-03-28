from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate

def get_tools(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    language: Optional[str] = None
) -> Tuple[List[Tool], int]:
    """Get tools with filtering and pagination."""
    query = db.query(Tool).filter(Tool.creator_id == user_id)
    
    # Apply filters
    if language:
        query = query.filter(Tool.language == language)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    tools = query.order_by(Tool.updated_at.desc()).offset(skip).limit(limit).all()
    
    return tools, total

def get_tool_by_id(db: Session, tool_id: str, user_id: str) -> Optional[Tool]:
    """Get a tool by ID with user check."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    
    # Check if tool exists and belongs to user
    if tool is None or tool.creator_id != user_id:
        return None
    
    return tool

def create_tool(db: Session, tool_in: ToolCreate, user_id: str) -> Tool:
    """Create a new tool."""
    # Create tool
    db_tool = Tool(
        id=str(uuid4()),
        name=tool_in.name,
        description=tool_in.description,
        code=tool_in.code,
        language=tool_in.language,
        creator_id=user_id
    )
    
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    
    return db_tool

def update_tool(db: Session, tool: Tool, tool_in: ToolUpdate) -> Tool:
    """Update a tool."""
    update_data = tool_in.dict(exclude_unset=True)
    
    # Update tool attributes
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    # Update timestamp
    tool.updated_at = datetime.utcnow()
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    return tool

def delete_tool(db: Session, tool_id: str) -> None:
    """Delete a tool."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    db.delete(tool)
    db.commit()

def test_tool(tool: Tool, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Test a tool with given parameters.
    
    In a real application, this would execute the tool code in a sandboxed environment.
    For now, we'll just return a mock response.
    """
    # Mock execution result
    return {
        "success": True,
        "result": f"Tool '{tool.name}' executed with parameters: {parameters}",
        "execution_time": "0.2s"
    }
