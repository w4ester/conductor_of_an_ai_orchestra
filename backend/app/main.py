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
