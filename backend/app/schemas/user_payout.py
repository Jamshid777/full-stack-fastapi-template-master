from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserPayoutBase(BaseModel):
    user_id: int
    amount: float
    source: str
    payout_date: date

class UserPayoutCreate(UserPayoutBase):
    pass

class UserPayoutOut(BaseModel):
    id: int
    user_id: int
    amount: float
    source: str
    payout_date: date

    class Config:
        from_attributes = True

class UserBalanceItem(BaseModel):
    id: int
    full_name: str
    share_percentage: float
    total_earnings: float
    total_payouts: float
    current_balance: float

class UserBalancesResponse(BaseModel):
    users: List[UserBalanceItem]