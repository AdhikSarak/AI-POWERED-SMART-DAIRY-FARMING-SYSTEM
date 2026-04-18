from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MilkAnalysisInput(BaseModel):
    cow_id: int
    ph: float = Field(..., ge=3.0, le=9.5, description="pH value of milk (3.0 - 9.5)")
    temperature: float = Field(..., ge=34.0, le=100.0, description="Temperature in Celsius")
    taste: int = Field(..., ge=0, le=1, description="0=Bad, 1=Good")
    odor: int = Field(..., ge=0, le=1, description="0=Bad, 1=Good")
    fat: float = Field(..., ge=0.1, le=10.0, description="Fat percentage")
    turbidity: int = Field(..., ge=0, le=1, description="0=Low, 1=High")
    colour: int = Field(..., ge=0, le=255, description="Colour value (0-255)")


class MilkRecordResponse(BaseModel):
    id: int
    cow_id: int
    ph: float
    temperature: float
    taste: int
    odor: int
    fat: float
    turbidity: int
    colour: int
    quality_grade: str
    quality_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class MilkAnalysisResult(BaseModel):
    cow_id: int
    quality_grade: str
    quality_score: float
    record_id: int
    input_parameters: dict
