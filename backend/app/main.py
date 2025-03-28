from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os

from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi import HTTPException, status

from app.db.database import get_db, engine, Base
from app.models.user import User
from app.services import user_service
from app.schemas.user import User as UserSchema, UserCreate
from app.schemas.token import Token, TokenData
from app.core.security import (
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.api.dependencies.auth import get_current_user, get_current_active_user
from app.api.v1 import api_router

# Create app
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

# Ollama API URL
OLLAMA_API_URL = "http://localhost:11434/api"

# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Return token and user info
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user
    }

@app.post("/api/users/register", response_model=UserSchema)
async def register_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    # Only admins can register new users for now
    db_user = user_service.get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return user_service.create_user(db, user_data)

# Add a public healthcheck endpoint that doesn't require authentication
@app.get("/api/public/health")
async def public_health_check():
    return {"status": "ok", "api_version": "0.1.0"}

# Helper function to verify token
def verify_token(token: str):
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return {"valid": False, "error": "Invalid token: missing subject"}
        return {"valid": True, "user_id": user_id}
    except JWTError as e:
        return {"valid": False, "error": f"Invalid token: {str(e)}"}

# Enhance the debug endpoint to help troubleshoot authentication issues
@app.get("/api/public/auth-debug")
async def auth_debug(request: Request, db: Session = Depends(get_db)):
    headers = dict(request.headers)
    auth_token = None
    token_info = {"valid": False, "error": "No token provided"}
    
    # Extract token from authorization header
    if "authorization" in headers:
        auth_header = headers["authorization"]
        headers["authorization"] = "Bearer [redacted]"  # Redact in response
        
        if auth_header.startswith("Bearer "):
            auth_token = auth_header.replace("Bearer ", "")
            token_info = verify_token(auth_token)
            
            # If token is valid, check if user exists
            if token_info["valid"] and "user_id" in token_info:
                user = db.query(User).filter(User.id == token_info["user_id"]).first()
                if user:
                    token_info["user_exists"] = True 
                    token_info["username"] = user.username
                else:
                    token_info["user_exists"] = False
    
    # Count users in database
    user_count = db.query(User).count()
    
    return {
        "headers": headers,
        "user_count": user_count,
        "token_info": token_info,
        "database_initialized": user_count > 0,
        "server_time": datetime.utcnow().isoformat()
    }

# Include API routers
app.include_router(api_router)

# Set up basic admin user and default tools on startup
@app.on_event("startup")
async def startup():
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    from app.db.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Check if users exist, create admin if not
        from app.models.user import User
        from app.core.security import get_password_hash
        from uuid import uuid4
        
        admin = db.query(User).filter(User.is_admin == True).first()
        if not admin:
            # No admin exists, create one
            admin = User(
                id=str(uuid4()),
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("password"),  # Change in production!
                is_admin=True,
                disabled=False
            )
            db.add(admin)
            db.commit()
            print("Created default admin user")
        
        # Set up default tools
        from app.utils.setup_default_tools import setup_default_tools
        tools = setup_default_tools(db)
        if tools:
            print(f"Created {len(tools)} default tools")
            
        # Set up default prompts
        from app.utils.setup_default_prompts import setup_default_prompts
        prompts = setup_default_prompts(db)
        if prompts:
            print(f"Created {len(prompts)} default prompts")
            
        # Set up default vector database collections
        from app.utils.setup_default_collections import setup_default_collections
        collections = setup_default_collections(db)
        if collections:
            print(f"Created {len(collections)} default collections")
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)