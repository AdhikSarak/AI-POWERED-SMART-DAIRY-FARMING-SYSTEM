from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CowCreate(BaseModel):
    cow_uid: Optional[str] = None
    name: str
    age: float
    breed: str
    weight_kg: Optional[float] = None


class CowUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[float] = None
    breed: Optional[str] = None
    weight_kg: Optional[float] = None


class CowResponse(BaseModel):
    id: int
    cow_uid: str
    name: str
    age: float
    breed: str
    weight_kg: Optional[float]
    farmer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
