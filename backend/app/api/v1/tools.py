from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.tool import ToolCreate, ToolUpdate, Tool, ToolList
from app.services.tool_service import (
    get_tools, get_tool_by_id, create_tool, 
    update_tool, delete_tool, test_tool
)

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])

@router.get("", response_model=ToolList)
async def list_all_tools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    language: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tools for the current user with filtering and pagination."""
    tools, total = get_tools(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit, 
        language=language
    )
    return {"items": tools, "total": total}

@router.get("/list")
async def list_available_tools_for_chat(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all available tools that can be used in chat."""
    # For now, just return a list of tools from the database
    tools, _ = get_tools(db, user_id=current_user.id)
    # Convert to format expected by frontend
    result = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {}  # This would need to be parsed from the tool code in a real implementation
        }
        for tool in tools
    ]
    return result

@router.get("/{tool_id}", response_model=Tool)
async def get_tool(
    tool_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific tool by ID."""
    tool = get_tool_by_id(db, tool_id, current_user.id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.post("", response_model=Tool, status_code=201)
async def create_new_tool(
    tool_in: ToolCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new tool."""
    return create_tool(db, tool_in, current_user.id)

@router.put("/{tool_id}", response_model=Tool)
async def update_existing_tool(
    tool_id: str = Path(...),
    tool_in: ToolUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing tool."""
    tool = get_tool_by_id(db, tool_id, current_user.id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return update_tool(db, tool, tool_in)

@router.delete("/{tool_id}", status_code=204)
async def delete_existing_tool(
    tool_id: str = Path(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a tool."""
    tool = get_tool_by_id(db, tool_id, current_user.id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    delete_tool(db, tool_id)
    return None

@router.post("/{tool_id}/test")
async def test_existing_tool(
    tool_id: str = Path(...),
    parameters: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test a tool with given parameters."""
    tool = get_tool_by_id(db, tool_id, current_user.id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return test_tool(tool, parameters)
