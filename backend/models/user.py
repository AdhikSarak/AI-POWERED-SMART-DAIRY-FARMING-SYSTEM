from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, index=True, nullable=False)
    phone      = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role       = Column(Enum("farmer", "admin", name="user_role"), default="farmer", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cows             = relationship("Cow",            back_populates="farmer", cascade="all, delete-orphan")
    milk_collections = relationship("MilkCollection", back_populates="farmer", cascade="all, delete-orphan")
    bills            = relationship("Billing",         back_populates="farmer", cascade="all, delete-orphan")
