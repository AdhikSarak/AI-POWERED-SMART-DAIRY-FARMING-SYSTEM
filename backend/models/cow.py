from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Cow(Base):
    __tablename__ = "cows"

    id         = Column(Integer, primary_key=True, index=True)
    cow_uid    = Column(String(50), unique=True, index=True, nullable=False)
    name       = Column(String(100), nullable=False)
    age        = Column(Float, nullable=False)
    breed      = Column(String(100), nullable=False)
    weight_kg  = Column(Float, nullable=True)
    farmer_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer          = relationship("User",           back_populates="cows")
    health_records  = relationship("HealthRecord",   back_populates="cow", cascade="all, delete-orphan")
    milk_records    = relationship("MilkRecord",     back_populates="cow", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="cow", cascade="all, delete-orphan")
