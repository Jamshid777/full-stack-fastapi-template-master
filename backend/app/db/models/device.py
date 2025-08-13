from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(255), primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    os = Column(String(100))
    last_seen = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    branch = relationship("Branch", back_populates="devices")