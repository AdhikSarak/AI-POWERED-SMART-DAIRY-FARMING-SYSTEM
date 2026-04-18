from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id           = Column(Integer, primary_key=True, index=True)
    cow_id       = Column(Integer, ForeignKey("cows.id", ondelete="CASCADE"), nullable=False)
    rec_type     = Column(Enum("feeding", "medication", "preventive", "general", name="rec_type_enum"), nullable=False)
    content      = Column(Text, nullable=False)
    generated_by = Column(String(50), default="groq_llm")
    created_at   = Column(DateTime, default=datetime.utcnow)

    cow = relationship("Cow", back_populates="recommendations")
