from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    boss = Column(String(255), nullable=False)
    password_hash = Column(String, nullable=True)
    plan = Column(String(50), nullable=False, default="Free")
    registrator_id = Column(Integer, ForeignKey("users.id"))
    registration_date = Column(Date, nullable=False)
    plan_expiration_days = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    branches = relationship("Branch", back_populates="organization", cascade="all, delete-orphan")
    add_ons = relationship("AddOn", back_populates="organization", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="organization", cascade="all, delete-orphan")