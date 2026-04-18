from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class MilkRecord(Base):
    __tablename__ = "milk_records"

    id            = Column(Integer, primary_key=True, index=True)
    cow_id        = Column(Integer, ForeignKey("cows.id", ondelete="CASCADE"), nullable=False)
    ph            = Column(Float, nullable=False)
    temperature   = Column(Float, nullable=False)
    taste         = Column(Integer, nullable=False)   # 0 = Bad, 1 = Good
    odor          = Column(Integer, nullable=False)   # 0 = Bad, 1 = Good
    fat           = Column(Float, nullable=False)
    turbidity     = Column(Integer, nullable=False)   # 0 = Low, 1 = High
    colour        = Column(Integer, nullable=False)   # colour value
    quality_grade = Column(Enum("Good", "Average", "Poor", name="milk_quality_enum"), nullable=False)
    quality_score = Column(Float, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    cow = relationship("Cow", back_populates="milk_records")
