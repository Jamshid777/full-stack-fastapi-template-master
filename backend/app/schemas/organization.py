from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class OrganizationBase(BaseModel):
    name: str
    phone: str
    boss: str
    password: str
    plan: str = "Free"
    registrator_id: Optional[int] = None
    registration_date: date
    plan_expiration_days: int = 30
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    boss: Optional[str] = None
    password: Optional[str] = None
    plan: Optional[str] = None
    registrator_id: Optional[int] = None
    registration_date: Optional[date] = None
    plan_expiration_days: Optional[int] = None
    is_active: Optional[bool] = None

class OrganizationOut(BaseModel):
    id: int
    name: str
    phone: str
    boss: str
    plan: str
    registrator_id: Optional[int]
    registration_date: date
    plan_expiration_days: int
    is_active: bool
    branches: List["BranchOut"]
    password: Optional[str] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    phone: str
    password: str
    
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: OrganizationOut

class BranchBase(BaseModel):
    name: str
    location: str

class BranchCreate(BranchBase):
    pass

class BranchOut(BaseModel):
    id: int
    organization_id: int
    name: str
    location: str

    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    branch_id: int
    name: str
    os: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceOut(BaseModel):
    id: str
    branch_id: int
    name: str
    os: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class AddOnBase(BaseModel):
    type: str
    quantity: int
    monthly_price: float

class AddOnCreate(AddOnBase):
    pass

class AddOnOut(BaseModel):
    id: str
    organization_id: int
    type: str
    quantity: int
    monthly_price: float

    class Config:
        from_attributes = True

class OrganizationListResponse(BaseModel):
    items: List[OrganizationOut]
    total: int
    page: int
    size: int