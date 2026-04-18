from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from backend.database import get_db
from backend.models.cow import Cow
from backend.models.health_record import HealthRecord
from backend.models.milk_record import MilkRecord
from backend.core.dependencies import get_current_farmer
from backend.services.groq_service import agentic_analyze
from backend.models.user import User

router = APIRouter()


class AgenticInsight(BaseModel):
    section: str
    content: str


class AgenticResponse(BaseModel):
    cow_id: int
    cow_name: str
    insights: str
    model_used: str


@router.post("/analyze/{cow_id}", response_model=AgenticResponse)
def agentic_cow_analysis(
    cow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_farmer),
):
    cow = db.query(Cow).filter(Cow.id == cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    health_records = db.query(HealthRecord).filter(HealthRecord.cow_id == cow_id).order_by(HealthRecord.created_at.desc()).limit(5).all()
    milk_records   = db.query(MilkRecord).filter(MilkRecord.cow_id == cow_id).order_by(MilkRecord.created_at.desc()).limit(5).all()

    cow_context = {
        "name": cow.name, "breed": cow.breed, "age": cow.age, "weight_kg": cow.weight_kg,
        "health_history": [
            {"disease": h.disease_name, "confidence": h.confidence_score, "status": h.health_status, "date": str(h.created_at.date())}
            for h in health_records
        ],
        "milk_history": [
            {"grade": m.quality_grade, "score": m.quality_score, "ph": m.ph, "fat": m.fat, "date": str(m.created_at.date())}
            for m in milk_records
        ],
    }

    insights = agentic_analyze(cow_context)
    return AgenticResponse(cow_id=cow_id, cow_name=cow.name, insights=insights, model_used="llama-3.3-70b-versatile")
