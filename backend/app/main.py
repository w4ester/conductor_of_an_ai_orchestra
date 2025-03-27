from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import requests
import base64

app = FastAPI(
    title="Ollama Workshop API",
    description="API for the Ollama Workshop Platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
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
        response = requests.get(f"{OLLAMA_API_URL}/tags")
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
            }
        )
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
            json={"name": name}
        )
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
            json={"name": name}
        )
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
        response = requests.post(f"{OLLAMA_API_URL}/generate", json=request)
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
        response = requests.post(f"{OLLAMA_API_URL}/embeddings", json=request)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Prompt management endpoints
@app.get("/api/prompts", response_model=List[Prompt])
async def list_prompts(current_user: User = Depends(get_current_active_user)):
    # Return only prompts created by the current user or shared prompts
    user_prompts = [
        prompt for prompt_id, prompt in prompts_db.items()
        if prompt.created_by == current_user.email
    ]
    return user_prompts

@app.get("/api/prompts/{prompt_id}", response_model=Prompt)
async def get_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if prompt_id not in prompts_db:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt = prompts_db[prompt_id]
    
    # Check if user has access to this prompt
    if prompt.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this prompt")
    
    return prompt

@app.post("/api/prompts", response_model=Prompt)
async def create_prompt(
    prompt: Prompt,
    current_user: User = Depends(get_current_active_user)
):
    # Set creator and timestamps
    import uuid
    from datetime import datetime
    
    prompt_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    prompt.id = prompt_id
    prompt.created_by = current_user.email
    prompt.created_at = now
    prompt.updated_at = now
    
    # Save to database
    prompts_db[prompt_id] = prompt
    
    return prompt

@app.put("/api/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(
    prompt_id: str,
    prompt_update: Prompt,
    current_user: User = Depends(get_current_active_user)
):
    if prompt_id not in prompts_db:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    existing_prompt = prompts_db[prompt_id]
    
    # Check if user has access to this prompt
    if existing_prompt.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to update this prompt")
    
    # Update timestamp
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # Update prompt with new data but preserve id and creation info
    prompt_update.id = prompt_id
    prompt_update.created_by = existing_prompt.created_by
    prompt_update.created_at = existing_prompt.created_at
    prompt_update.updated_at = now
    
    # Save to database
    prompts_db[prompt_id] = prompt_update
    
    return prompt_update

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if prompt_id not in prompts_db:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompt = prompts_db[prompt_id]
    
    # Check if user has access to this prompt
    if prompt.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this prompt")
    
    # Delete from database
    del prompts_db[prompt_id]
    
    return {"message": "Prompt deleted successfully"}

# Tool management endpoints
@app.get("/api/tools", response_model=List[Tool])
async def list_tools(current_user: User = Depends(get_current_active_user)):
    # Return only tools created by the current user or shared tools
    user_tools = [
        tool for tool_id, tool in tools_db.items()
        if tool.created_by == current_user.email
    ]
    return user_tools

@app.get("/api/tools/{tool_id}", response_model=Tool)
async def get_tool(
    tool_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if tool_id not in tools_db:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool = tools_db[tool_id]
    
    # Check if user has access to this tool
    if tool.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this tool")
    
    return tool

@app.post("/api/tools", response_model=Tool)
async def create_tool(
    tool: Tool,
    current_user: User = Depends(get_current_active_user)
):
    # Set creator and timestamps
    import uuid
    from datetime import datetime
    
    tool_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    tool.id = tool_id
    tool.created_by = current_user.email
    tool.created_at = now
    tool.updated_at = now
    
    # Save to database
    tools_db[tool_id] = tool
    
    return tool

@app.put("/api/tools/{tool_id}", response_model=Tool)
async def update_tool(
    tool_id: str,
    tool_update: Tool,
    current_user: User = Depends(get_current_active_user)
):
    if tool_id not in tools_db:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    existing_tool = tools_db[tool_id]
    
    # Check if user has access to this tool
    if existing_tool.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to update this tool")
    
    # Update timestamp
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # Update tool with new data but preserve id and creation info
    tool_update.id = tool_id
    tool_update.created_by = existing_tool.created_by
    tool_update.created_at = existing_tool.created_at
    tool_update.updated_at = now
    
    # Save to database
    tools_db[tool_id] = tool_update
    
    return tool_update

@app.delete("/api/tools/{tool_id}")
async def delete_tool(
    tool_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if tool_id not in tools_db:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool = tools_db[tool_id]
    
    # Check if user has access to this tool
    if tool.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tool")
    
    # Delete from database
    del tools_db[tool_id]
    
    return {"message": "Tool deleted successfully"}

@app.post("/api/tools/{tool_id}/test")
async def test_tool(
    tool_id: str,
    request: Dict,
    current_user: User = Depends(get_current_active_user)
):
    if tool_id not in tools_db:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool = tools_db[tool_id]
    
    # Check if user has access to this tool
    if tool.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to test this tool")
    
    # In a real application, we would execute the tool safely
    # For now, we'll just return a mock response
    
    # Get the parameters from the request
    input_params = request.get("parameters", {})
    
    # Mock execution result
    result = {
        "success": True,
        "result": f"Tool executed with parameters: {input_params}",
        "execution_time": "0.2s"
    }
    
    return result

# Document management endpoints
from fastapi import UploadFile, File
import base64

@app.get("/api/documents", response_model=List[Document])
async def list_documents(current_user: User = Depends(get_current_active_user)):
    # Return only documents created by the current user
    user_documents = [
        document for doc_id, document in documents_db.items()
        if document.created_by == current_user.email
    ]
    return user_documents

@app.get("/api/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = documents_db[document_id]
    
    # Check if user has access to this document
    if document.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    return document

@app.post("/api/documents", response_model=Document)
async def create_document(
    document: Document,
    current_user: User = Depends(get_current_active_user)
):
    # Set creator and timestamps
    import uuid
    from datetime import datetime
    
    document_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    document.id = document_id
    document.created_by = current_user.email
    document.created_at = now
    
    # Save to database
    documents_db[document_id] = document
    
    return document

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    # Set creator and timestamps
    import uuid
    from datetime import datetime
    import io
    
    document_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Read file content
    file_content = await file.read()
    
    # Determine file type from extension
    file_extension = file.filename.split('.')[-1].lower()
    
    # Create document object
    document = Document(
        id=document_id,
        title=title or file.filename,
        content=base64.b64encode(file_content).decode('utf-8'),
        file_type=file_extension,
        created_by=current_user.email,
        created_at=now
    )
    
    # Save to database
    documents_db[document_id] = document
    
    return document

@app.post("/api/documents/{document_id}/extract")
async def extract_document_text(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = documents_db[document_id]
    
    # Check if user has access to this document
    if document.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Decode the base64 content
    content_bytes = base64.b64decode(document.content)
    
    # In a real application, we would use libraries like PyPDF2, docx, etc.
    # to extract text based on file_type
    # For demonstration, we'll just return a mock extraction
    
    # Mock text extraction based on file type
    if document.file_type == 'pdf':
        text = f"Extracted text from PDF: {document.title}"
    elif document.file_type == 'docx':
        text = f"Extracted text from Word document: {document.title}"
    elif document.file_type == 'txt':
        text = content_bytes.decode('utf-8')
    else:
        text = f"Extracted text from {document.file_type.upper()} file: {document.title}"
    
    return {"text": text, "document_id": document_id}

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = documents_db[document_id]
    
    # Check if user has access to this document
    if document.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    # Delete from database
    del documents_db[document_id]
    
    return {"message": "Document deleted successfully"}

# Vector Database and Embedding endpoints
class VectorDatabase(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    connection_string: Optional[str] = None
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Embedding(BaseModel):
    id: Optional[str] = None
    document_id: str
    vector_db_id: str
    model: str
    dimensions: int
    created_by: str
    created_at: Optional[str] = None
    chunks: Optional[List[Dict]] = []

class EmbeddingRequest(BaseModel):
    document_id: str
    vector_db_id: str
    model: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

# In-memory storage for vector databases and embeddings
vector_dbs = {}
embeddings_db = {}

@app.get("/api/vector-dbs", response_model=List[VectorDatabase])
async def list_vector_dbs(current_user: User = Depends(get_current_active_user)):
    # Return only vector databases created by the current user
    user_dbs = [
        db for db_id, db in vector_dbs.items()
        if db.created_by == current_user.email
    ]
    return user_dbs

@app.post("/api/vector-dbs", response_model=VectorDatabase)
async def create_vector_db(
    db: VectorDatabase,
    current_user: User = Depends(get_current_active_user)
):
    # Set creator and timestamps
    import uuid
    from datetime import datetime
    
    db_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    db.id = db_id
    db.created_by = current_user.email
    db.created_at = now
    db.updated_at = now
    
    # Save to database
    vector_dbs[db_id] = db
    
    return db

@app.get("/api/vector-dbs/{db_id}", response_model=VectorDatabase)
async def get_vector_db(
    db_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if db_id not in vector_dbs:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    db = vector_dbs[db_id]
    
    # Check if user has access to this vector database
    if db.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this vector database")
    
    return db

@app.delete("/api/vector-dbs/{db_id}")
async def delete_vector_db(
    db_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if db_id not in vector_dbs:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    db = vector_dbs[db_id]
    
    # Check if user has access to this vector database
    if db.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this vector database")
    
    # Delete from database
    del vector_dbs[db_id]
    
    return {"message": "Vector database deleted successfully"}

@app.get("/api/embeddings", response_model=List[Embedding])
async def list_embeddings(current_user: User = Depends(get_current_active_user)):
    # Return only embeddings created by the current user
    user_embeddings = [
        embedding for emb_id, embedding in embeddings_db.items()
        if embedding.created_by == current_user.email
    ]
    return user_embeddings

@app.get("/api/embeddings/{embedding_id}", response_model=Embedding)
async def get_embedding(
    embedding_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if embedding_id not in embeddings_db:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    embedding = embeddings_db[embedding_id]
    
    # Check if user has access to this embedding
    if embedding.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this embedding")
    
    return embedding

@app.post("/api/embeddings", response_model=Embedding)
async def create_embedding(
    request: EmbeddingRequest,
    current_user: User = Depends(get_current_active_user)
):
    # Verify document exists
    if request.document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify vector database exists
    if request.vector_db_id not in vector_dbs:
        raise HTTPException(status_code=404, detail="Vector database not found")
    
    # Get the document
    document = documents_db[request.document_id]
    
    # Check if user has access to the document
    if document.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Extract text from document
    # In a real application, we would extract text based on file type
    # For demonstration, we'll mock this
    
    # Create chunks
    # In a real application, we would use a proper chunking algorithm
    # For demonstration, we'll create mock chunks
    chunks = [
        {"text": f"Chunk {i} from document {document.title}", "metadata": {"position": i}}
        for i in range(1, 6)  # Mock 5 chunks
    ]
    
    # Create embeddings for each chunk
    # In a real application, we would use an embedding model to create real embeddings
    # For demonstration, we'll create mock embeddings with random values
    import uuid
    from datetime import datetime
    import random
    
    # Set the dimensions based on the model
    dimensions = 384  # Default dimensions for most models
    if "large" in request.model.lower():
        dimensions = 768
    elif "small" in request.model.lower():
        dimensions = 256
    
    embedding_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    embedding = Embedding(
        id=embedding_id,
        document_id=request.document_id,
        vector_db_id=request.vector_db_id,
        model=request.model,
        dimensions=dimensions,
        created_by=current_user.email,
        created_at=now,
        chunks=chunks
    )
    
    # Save to database
    embeddings_db[embedding_id] = embedding
    
    return embedding

@app.delete("/api/embeddings/{embedding_id}")
async def delete_embedding(
    embedding_id: str,
    current_user: User = Depends(get_current_active_user)
):
    if embedding_id not in embeddings_db:
        raise HTTPException(status_code=404, detail="Embedding not found")
    
    embedding = embeddings_db[embedding_id]
    
    # Check if user has access to this embedding
    if embedding.created_by != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this embedding")
    
    # Delete from database
    del embeddings_db[embedding_id]
    
    return {"message": "Embedding deleted successfully"}

@app.get("/api/embedding-models")
async def list_embedding_models(current_user: User = Depends(get_current_active_user)):
    # In a real application, we would get this from Ollama or another source
    # For demonstration, we'll return a list of common embedding models
    models = [
        {"name": "nomic-embed-text", "dimensions": 768, "description": "General purpose text embedding model"},
        {"name": "all-minilm-l6-v2", "dimensions": 384, "description": "Fast, efficient embedding model"},
        {"name": "e5-small-v2", "dimensions": 384, "description": "Small, efficient text embedding model"},
        {"name": "e5-large-v2", "dimensions": 1024, "description": "Large, high-quality text embedding model"},
        {"name": "bge-small-en", "dimensions": 384, "description": "BGE small model for English text"},
        {"name": "bge-large-en", "dimensions": 1024, "description": "BGE large model for English text"}
    ]
    
    return models

@app.get("/api/vector-db-types")
async def list_vector_db_types(current_user: User = Depends(get_current_active_user)):
    # In a real application, we would get this from available integrations
    # For demonstration, we'll return a list of common vector database types
    db_types = [
        {"name": "chroma", "description": "Open-source vector database with simple API"},
        {"name": "pinecone", "description": "Managed vector database service with advanced features"},
        {"name": "qdrant", "description": "Open-source vector search engine"},
        {"name": "weaviate", "description": "Vector database with rich semantic search capabilities"},
        {"name": "milvus", "description": "Open-source vector database for AI applications"},
        {"name": "redis", "description": "In-memory database with vector search capabilities"},
        {"name": "pgvector", "description": "PostgreSQL extension for vector similarity search"}
    ]
    
    return db_types

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)