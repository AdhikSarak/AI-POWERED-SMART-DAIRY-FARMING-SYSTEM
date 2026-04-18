from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class MilkCollectionCreate(BaseModel):
    farmer_id: int
    quantity_liters: float = Field(..., gt=0)
    quality_grade: str
    rate_per_liter: float = Field(..., gt=0)
    collection_date: date
    notes: Optional[str] = None


class MilkCollectionResponse(BaseModel):
    id: int
    farmer_id: int
    quantity_liters: float
    quality_grade: str
    rate_per_liter: float
    collection_date: date
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BillingResponse(BaseModel):
    id: int
    farmer_id: int
    month: str
    total_liters: float
    total_amount: float
    bill_pdf_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateBillRequest(BaseModel):
    farmer_id: int
    month: str   # e.g. "2024-04"
