from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Billing(Base):
    __tablename__ = "billing"

    id             = Column(Integer, primary_key=True, index=True)
    farmer_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    month          = Column(String(20), nullable=False)   # e.g. "2024-04"
    total_liters   = Column(Float, nullable=False)
    total_amount   = Column(Float, nullable=False)
    bill_pdf_path  = Column(String(500), nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="bills")
