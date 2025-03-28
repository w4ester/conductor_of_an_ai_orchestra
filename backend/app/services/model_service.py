import requests
from typing import Dict, List, Any
import os

# Configuration for Ollama API
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")

def list_models() -> List[Dict]:
    """Get a list of available models from Ollama."""
    response = requests.get(f"{OLLAMA_API_URL}/tags")
    response.raise_for_status()
    return response.json().get("models", [])

def create_model(name: str, modelfile: str) -> Dict:
    """Create a new model using Ollama API."""
    response = requests.post(
        f"{OLLAMA_API_URL}/create", 
        json={
            "name": name,
            "modelfile": modelfile
        }
    )
    response.raise_for_status()
    return {"success": True, "message": f"Model {name} created successfully"}

def get_modelfile(name: str) -> Dict:
    """Get the Modelfile for a model."""
    response = requests.post(
        f"{OLLAMA_API_URL}/show", 
        json={"name": name}
    )
    response.raise_for_status()
    data = response.json()
    return {"modelfile": data.get("modelfile", "")}

def delete_model(name: str) -> Dict:
    """Delete a model."""
    response = requests.delete(
        f"{OLLAMA_API_URL}/delete", 
        json={"name": name}
    )
    response.raise_for_status()
    return {"success": True, "message": f"Model {name} deleted successfully"}

def generate(request: Dict) -> Dict:
    """Generate text using Ollama API."""
    response = requests.post(f"{OLLAMA_API_URL}/generate", json=request)
    response.raise_for_status()
    return response.json()

def get_embeddings(request: Dict) -> Dict:
    """Get embeddings using Ollama API."""
    response = requests.post(f"{OLLAMA_API_URL}/embeddings", json=request)
    response.raise_for_status()
    return response.json()
