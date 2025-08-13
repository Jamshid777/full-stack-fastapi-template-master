from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, CheckConstraint, ARRAY
from sqlalchemy.sql import func
from app.db.base import Base

class CustomPlan(Base):
    __tablename__ = "custom_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    branches = Column(Integer, default=1)
    devices_per_branch = Column(Integer, default=1)
    waiters = Column(Integer, default=0)
    kds = Column(Boolean, default=False)
    warehouse_control = Column(String(20), default="none")
    tech_card = Column(String(20), default="none")
    chat_support = Column(Boolean, default=False)
    api_integrations = Column(ARRAY(String))
    phone_support_247 = Column(Boolean, default=False)
    personal_manager = Column(Boolean, default=False)
    monthly_price = Column(Numeric(12, 2), default=0.00)
    yearly_price = Column(Numeric(12, 2), default=0.00)
    flag = Column(String(50))
    color = Column(String(7))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("warehouse_control in ('none','lite','pro')", name="warehouse_control_check"),
        CheckConstraint("tech_card in ('none','lite','pro')", name="tech_card_check"),
    )