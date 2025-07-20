from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    is_active: bool | None = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass 