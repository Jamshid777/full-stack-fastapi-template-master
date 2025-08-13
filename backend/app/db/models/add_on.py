from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class AddOn(Base):
    __tablename__ = "add_ons"

    id = Column(String(255), primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    type = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    monthly_price = Column(Numeric(12, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="add_ons")

    __table_args__ = (
        CheckConstraint("type in ('branch','device','waiter')", name="add_ons_type_check"),
    )