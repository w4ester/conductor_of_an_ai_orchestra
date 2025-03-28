import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any

from app.api.dependencies.users import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.services.tool_service import get_tools_for_model
from app.services.prompt_service import get_prompt_by_id

# Ollama API URL
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

# OpenAI API details (will be used in future implementations)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/generate")
async def generate_chat_response(
    request: Dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate chat response with optional tool support."""
    try:
        model = request.get("model", "")
        prompt = request.get("prompt", "")
        system = request.get("system", "")
        tools_enabled = request.get("tools", False)
        selected_tools = request.get("selectedTools", [])
        context = request.get("context", [])

        # Get system prompt if prompt_id is provided
        if system and system.startswith("prompt:"):
            prompt_id = system.replace("prompt:", "")
            prompt_obj = get_prompt_by_id(db, prompt_id)
            if prompt_obj:
                system = prompt_obj.content
        
        # Check if model is an OpenAI model (for future implementation)
        if model.startswith("openai:"):
            # TODO: implement OpenAI API integration
            raise HTTPException(status_code=501, detail="OpenAI integration not implemented yet")
        
        # Default to Ollama for local models
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        
        # Add context if provided
        if context:
            # Format context as required by Ollama
            if isinstance(context, list):
                # The frontend may send a formatted context in the format Ollama expects
                ollama_request["context"] = context
            else:
                # Or we might need to format it
                ollama_request["context"] = []
        
        # Handle tools if enabled
        if tools_enabled and selected_tools:
            # Load available tools
            available_tools = get_tools_for_model(db, current_user.id, selected_tools)
            
            # If we have tools, augment the system prompt
            if available_tools:
                # Add tool information to system prompt
                tools_description = "You have access to the following tools:\n"
                for tool in available_tools:
                    tools_description += f"- {tool.name}: {tool.description}\n"
                
                # Append tool instructions to system prompt
                if system:
                    ollama_request["system"] = system + "\n\n" + tools_description
                else:
                    ollama_request["system"] = tools_description
        
        # Make the request to Ollama
        response = requests.post(
            f"{OLLAMA_API_URL}/generate", 
            json=ollama_request,
            timeout=180  # Add a 180-second timeout
        )
        
        # Check for errors
        if not response.ok:
            error_msg = "Error from Ollama API"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"]
            except:
                pass
            raise HTTPException(status_code=response.status_code, detail=error_msg)
            
        result = response.json()
        
        # Process the response
        response_text = result.get("response", "")
        output_context = result.get("context", [])
        
        # Parse the response for potential tool calls (in a future implementation)
        # Here you would analyze the response_text to determine if tools need to be called
        tool_calls = []  # Placeholder for future tool extraction logic
        
        return {
            "response": response_text,
            "context": output_context,
            "tool_calls": tool_calls
        }
    except Exception as e:
        # Handle exceptions
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")


# Function to implement in tool_service.py (we need to create this)
def get_tools_for_model(db: Session, user_id: str, selected_tools: List[str]):
    """
    Get tools by their names that the user has access to.
    This is a placeholder - you should implement this in the tool_service.py file.
    """
    from app.models.tool import Tool
    # Get all tools that match the selected names and that the user has access to
    tools = db.query(Tool).filter(
        Tool.name.in_(selected_tools),
        Tool.creator_id == user_id
    ).all()
    return tools
