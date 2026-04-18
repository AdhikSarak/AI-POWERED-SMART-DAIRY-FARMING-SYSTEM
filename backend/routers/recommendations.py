from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.cow import Cow
from backend.models.health_record import HealthRecord
from backend.models.milk_record import MilkRecord
from backend.models.recommendation import Recommendation
from backend.core.dependencies import get_current_farmer
from backend.services.groq_service import generate_recommendation
from backend.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class RecommendationResponse(BaseModel):
    id: int
    cow_id: int
    rec_type: str
    content: str
    generated_by: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate/{cow_id}", response_model=List[RecommendationResponse])
def generate_recommendations(
    cow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_farmer),
):
    cow = db.query(Cow).filter(Cow.id == cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    latest_health = db.query(HealthRecord).filter(HealthRecord.cow_id == cow_id).order_by(HealthRecord.created_at.desc()).first()
    latest_milk   = db.query(MilkRecord).filter(MilkRecord.cow_id == cow_id).order_by(MilkRecord.created_at.desc()).first()

    cow_data = {
        "name": cow.name, "breed": cow.breed, "age": cow.age,
        "disease": latest_health.disease_name if latest_health else "No recent health check",
        "health_status": latest_health.health_status if latest_health else "Unknown",
        "milk_quality": latest_milk.quality_grade if latest_milk else "No recent milk test",
        "milk_ph": latest_milk.ph if latest_milk else None,
        "milk_fat": latest_milk.fat if latest_milk else None,
    }

    recommendations = generate_recommendation(cow_data)
    saved = []
    for rec in recommendations:
        obj = Recommendation(cow_id=cow_id, rec_type=rec["type"], content=rec["content"])
        db.add(obj)
        db.commit()
        db.refresh(obj)
        saved.append(obj)
    return saved


@router.get("/{cow_id}", response_model=List[RecommendationResponse])
def get_recommendations(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    return db.query(Recommendation).filter(Recommendation.cow_id == cow_id).order_by(Recommendation.created_at.desc()).all()
