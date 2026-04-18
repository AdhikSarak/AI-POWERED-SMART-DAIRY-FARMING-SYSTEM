from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HealthRecordResponse(BaseModel):
    id: int
    cow_id: int
    image_path: Optional[str]
    disease_name: str
    confidence_score: float
    health_status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthAnalysisResult(BaseModel):
    cow_id: int
    disease_name: str
    confidence_score: float
    health_status: str
    all_predictions: dict
    record_id: int
