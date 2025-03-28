from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from uuid import uuid4

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_users(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
    """Get all users with pagination."""
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return users, total

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user."""
    # Check if email already exists
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        id=str(uuid4()),
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_admin=False,
        disabled=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Update a user."""
    update_data = user_in.dict(exclude_unset=True)
    
    # Check if email is being updated and is already taken
    if "email" in update_data and update_data["email"] != user.email:
        if get_user_by_email(db, update_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is being updated and is already taken
    if "username" in update_data and update_data["username"] != user.username:
        if get_user_by_username(db, update_data["username"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Handle password hashing if it's being updated
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    # Update user attributes
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(db: Session, user_id: str) -> None:
    """Delete a user."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
