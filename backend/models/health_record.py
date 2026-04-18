from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"

    id               = Column(Integer, primary_key=True, index=True)
    cow_id           = Column(Integer, ForeignKey("cows.id", ondelete="CASCADE"), nullable=False)
    image_path       = Column(String(500), nullable=True)
    disease_name     = Column(String(200), nullable=False)
    confidence_score = Column(Float, nullable=False)
    health_status    = Column(Enum("Healthy", "Diseased", name="health_status_enum"), nullable=False)
    notes            = Column(String(500), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    cow = relationship("Cow", back_populates="health_records")
