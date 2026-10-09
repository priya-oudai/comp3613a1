from app.models.user import UserBase
from sqlmodel import SQLModel
from typing import Optional


class UserUpdate(SQLModel):
    username: Optional[str]
 
class AdminCreate(UserBase):
    role:str = "admin"

class RegularUserCreate(UserBase):
    role:str = "student"

class OwnerCreate(UserBase):
    role:str = "owner"

class UserResponse(SQLModel):
    id: int
    username:str

class SignupRequest(SQLModel):
    username: str
    password: str
    role: str
