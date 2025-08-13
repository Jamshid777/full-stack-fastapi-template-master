from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, CheckConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    address = Column(Text)
    role = Column(String(20), nullable=False, default="registrator")
    share_percentage = Column(Numeric(5, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('admin','registrator','moderator')", name="users_role_check"),
    )