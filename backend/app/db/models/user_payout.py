from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class UserPayout(Base):
    __tablename__ = "user_payouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Numeric(12, 2), nullable=False)
    source = Column(String(20), nullable=False)
    payout_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("source in ('O''tkazma', 'Naqd pul')", name="user_payouts_source_check"),
    )