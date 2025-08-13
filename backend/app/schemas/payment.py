from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class PaymentBase(BaseModel):
    organization_id: int
    amount: float
    source: str
    payment_date: date

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(BaseModel):
    id: int
    organization_id: int
    amount: float
    source: str
    payment_date: date

    class Config:
        from_attributes = True

class PaymentListResponse(BaseModel):
    items: List[PaymentOut]
    total: int
    page: int
    size: int

class SverkaItem(BaseModel):
    date: date
    total_amount: float

class SverkaResponse(BaseModel):
    organization_id: int
    start_date: date
    end_date: date
    total_amount: float