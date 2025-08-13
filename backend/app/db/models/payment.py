from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    amount = Column(Numeric(12, 2), nullable=False)
    source = Column(String(50), nullable=False)
    payment_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="payments")

    __table_args__ = (
        CheckConstraint("source in ('Subscription','Click','Payme')", name="payments_source_check"),
    )