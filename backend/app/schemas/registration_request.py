from pydantic import BaseModel
from typing import Optional

class RegistrationRequestCreate(BaseModel):
    full_name: str
    phone: str
    password: str
    address: Optional[str] = None

class RegistrationRequestOut(BaseModel):
    id: int
    full_name: str
    phone: str
    address: Optional[str]
    status: str

    class Config:
        from_attributes = True

class RegistrationApprovePayload(BaseModel):
    share_percentage: float