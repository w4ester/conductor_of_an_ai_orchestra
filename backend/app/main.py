import time
import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Store application start time
os.environ["APP_START_TIME"] = str(time.time())

# Import API router
from app.api.v1 import auth, users, prompts, tools, documents, vector_dbs, embeddings, rag_systems, models

# Import database initialization
from app.db.database import Base, engine, get_db

# Import health checker
from app.utils.health import HealthChecker

# Import middleware
from app.middleware.logging import LoggingMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ollama Workshop API",
    description="API for the Ollama Workshop Platform",
    version="0.1.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Default Vite dev server
    "http://localhost:4173",  # Default Vite preview
    "http://localhost:3000",  # Alternative frontend
    "http://localhost:8080",  # Docker frontend
]

# Use environment variable in production
if os.getenv("CORS_ORIGINS"):
    origins.extend(os.getenv("CORS_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user database for demonstration
fake_users_db = {
    "user@example.com": {
        "email": "user@example.com",
        "username": "workshopuser",
        "full_name": "Workshop User",
        "hashed_password": "password",  # In a real app, this would be properly hashed
        "disabled": False,
    },
    "admin@example.com": {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Workshop Admin",
        "hashed_password": "admin",  # In a real app, this would be properly hashed
        "disabled": False,
        "is_admin": True
    }
}

# In-memory storage for prompts, tools, documents, and RAG systems
prompts_db = {}
tools_db = {}
documents_db = {}
rag_systems_db = {}

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class User(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class OllamaModel(BaseModel):
    name: str
    id: str
    size: str
    modified: str

class ModelList(BaseModel):
    models: List[OllamaModel]
    
class Prompt(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    model: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
class Tool(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    code: str
    language: str = "python"
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
class Document(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    file_type: str
    created_by: str
    created_at: Optional[str] = None
    
class RAGSystem(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    embedding_model: str
    documents: List[str]
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Authentication functions
def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, email: str, password: str):
    user = get_user(fake_db, email)
    if not user:
        return False
    # In a real app, you would verify the hashed password
    if password != user.hashed_password:
        return False
    return user

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real app, you would verify the JWT token
    # For demo purposes, we'll just check if the token matches a username
    user = get_user(fake_users_db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Routes
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real app, you would create a JWT token here
    # For demo purposes, we'll just return the email as the token
    return {"access_token": user.email, "token_type": "bearer"}

@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Ollama API
OLLAMA_API_URL = "http://localhost:11434/api"

@app.get("/api/models", response_model=List[Dict])
async def list_models(current_user: User = Depends(get_current_active_user)):
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=60)
        response.raise_for_status()
        return response.json().get("models", [])
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

@app.post("/api/models/create")
async def create_model(
    request: Dict,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Extract parameters from request
        name = request.get("name")
        modelfile = request.get("modelfile")
        
        if not name or not modelfile:
            raise HTTPException(status_code=400, detail="Name and modelfile are required")
        
        # Create model using Ollama API
        response = requests.post(
            f"{OLLAMA_API_URL}/create", 
            json={
                "name": name,
                "modelfile": modelfile
            }, 
        timeout=60)
        response.raise_for_status()
        return {"success": True, "message": f"Model {name} created successfully"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error creating model: {str(e)}")

@app.get("/api/models/{name}/modelfile")
async def get_modelfile(
    name: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Get the Modelfile for a model
        response = requests.post(
            f"{OLLAMA_API_URL}/show", 
            json={"name": name}, 
        timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Return the modelfile
        return {"modelfile": data.get("modelfile", "")}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error getting modelfile: {str(e)}")

@app.delete("/api/models/{name}")
async def delete_model(
    name: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Delete the model
        response = requests.delete(
            f"{OLLAMA_API_URL}/delete", 
            json={"name": name}, 
        timeout=60)
        response.raise_for_status()
        return {"success": True, "message": f"Model {name} deleted successfully"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")

@app.post("/api/generate")
async def generate(
    request: Dict, 
    current_user: User = Depends(get_current_active_user)
):
    try:
        response = requests.post(f"{OLLAMA_API_URL}/generate", json=request, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

@app.post("/api/embeddings")
async def get_embeddings(
    request: Dict, 
    current_user: User = Depends(get_current_active_user)
):
    try:
        response = requests.post(f"{OLLAMA_API_URL}/embeddings", json=request, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include API routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prompts.router)
app.include_router(tools.router)
app.include_router(documents.router)
app.include_router(vector_dbs.router)
app.include_router(embeddings.router)
app.include_router(rag_systems.router)
app.include_router(models.router)

# Health check endpoints
@app.get("/api/health")
async def health_check(request: Request, db: Session = Depends(get_db)):
    """Basic health check endpoint."""
    return {"status": "ok", "api_version": "0.1.0"}

@app.get("/api/health/detailed")
async def detailed_health_check(request: Request, db: Session = Depends(get_db)):
    """Detailed health check with component status."""
    return HealthChecker.check_all(db)

# Add public health endpoint that doesn't require authentication
@app.get("/api/public/health")
async def public_health_check():
    """Public health check endpoint (no auth required)."""
    return {"status": "ok", "api_version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
