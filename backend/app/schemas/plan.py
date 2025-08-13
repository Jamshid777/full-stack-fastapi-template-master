from pydantic import BaseModel
from typing import Optional, List

class PlanBase(BaseModel):
    name: str
    branches: int = 1
    devices_per_branch: int = 1
    waiters: int = 0
    kds: bool = False
    warehouse_control: str = "none"
    tech_card: str = "none"
    chat_support: bool = False
    api_integrations: List[str] = []
    phone_support_247: bool = False
    personal_manager: bool = False
    monthly_price: float = 0.0
    yearly_price: float = 0.0
    flag: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    branches: Optional[int] = None
    devices_per_branch: Optional[int] = None
    waiters: Optional[int] = None
    kds: Optional[bool] = None
    warehouse_control: Optional[str] = None
    tech_card: Optional[str] = None
    chat_support: Optional[bool] = None
    api_integrations: Optional[List[str]] = None
    phone_support_247: Optional[bool] = None
    personal_manager: Optional[bool] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None
    flag: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class PlanOut(BaseModel):
    id: int
    name: str
    branches: int
    devices_per_branch: int
    waiters: int
    kds: bool
    warehouse_control: str
    tech_card: str
    chat_support: bool
    api_integrations: List[str]
    phone_support_247: bool
    personal_manager: bool
    monthly_price: float
    yearly_price: float
    flag: Optional[str]
    color: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True