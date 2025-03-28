# app/schemas/user.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: str
    role: str
    is_active: bool
    approval_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class UserList(BaseModel):
    items: List[User]
    total: int
