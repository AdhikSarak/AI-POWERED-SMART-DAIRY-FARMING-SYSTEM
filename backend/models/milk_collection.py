from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class MilkCollection(Base):
    __tablename__ = "milk_collections"

    id               = Column(Integer, primary_key=True, index=True)
    farmer_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quantity_liters  = Column(Float, nullable=False)
    quality_grade    = Column(Enum("Good", "Average", "Poor", name="collection_quality_enum"), nullable=False)
    rate_per_liter   = Column(Float, nullable=False)
    collection_date  = Column(Date, nullable=False)
    notes            = Column(String(300), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="milk_collections")
