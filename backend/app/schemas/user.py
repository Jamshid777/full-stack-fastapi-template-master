from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    phone: str
    address: Optional[str] = None
    role: str = Field(default="registrator")
    share_percentage: float = 0.0

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    share_percentage: Optional[float] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    full_name: str
    phone: str
    role: str
    share_percentage: float
    address: Optional[str] = None
    

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    phone: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"