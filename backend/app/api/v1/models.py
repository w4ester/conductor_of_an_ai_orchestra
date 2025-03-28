from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Optional

from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.model_service import (
    list_models, create_model, get_modelfile, 
    delete_model, generate, get_embeddings
)

router = APIRouter(prefix="/api/v1/models", tags=["models"])

@router.get("", response_model=List[Dict])
async def get_model_list(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available Ollama models."""
    try:
        return list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

@router.post("/create")
async def create_new_model(
    request: Dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new Ollama model with a modelfile."""
    try:
        name = request.get("name")
        modelfile = request.get("modelfile")
        
        if not name or not modelfile:
            raise HTTPException(status_code=400, detail="Name and modelfile are required")
        
        return create_model(name, modelfile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating model: {str(e)}")

@router.get("/{name}/modelfile")
async def get_model_file(
    name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the modelfile for a specific model."""
    try:
        return get_modelfile(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting modelfile: {str(e)}")

@router.delete("/{name}")
async def delete_existing_model(
    name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an Ollama model."""
    try:
        return delete_model(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")
@router.post("/generate")
async def generate_text(
    request: Dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """Generate text using an Ollama model."""
    try:
        return generate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.post("/embeddings")
async def create_embeddings(
    request: Dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """Create embeddings using an Ollama model."""
    try:
        return get_embeddings(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")
