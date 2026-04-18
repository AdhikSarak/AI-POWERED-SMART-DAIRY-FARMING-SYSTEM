from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.cow import Cow
from backend.models.milk_record import MilkRecord
from backend.schemas.milk import MilkAnalysisInput, MilkRecordResponse, MilkAnalysisResult
from backend.core.dependencies import get_current_farmer
from backend.services.milk_service import predict_milk_quality
from backend.models.user import User

router = APIRouter()


@router.post("/analyze", response_model=MilkAnalysisResult)
def analyze_milk(
    payload: MilkAnalysisInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_farmer),
):
    cow = db.query(Cow).filter(Cow.id == payload.cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    features = {
        "ph": payload.ph,
        "temperature": payload.temperature,
        "taste": payload.taste,
        "odor": payload.odor,
        "fat": payload.fat,
        "turbidity": payload.turbidity,
        "colour": payload.colour,
    }
    result = predict_milk_quality(features)

    record = MilkRecord(
        cow_id=payload.cow_id,
        ph=payload.ph,
        temperature=payload.temperature,
        taste=payload.taste,
        odor=payload.odor,
        fat=payload.fat,
        turbidity=payload.turbidity,
        colour=payload.colour,
        quality_grade=result["grade"],
        quality_score=result["score"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return MilkAnalysisResult(
        cow_id=payload.cow_id,
        quality_grade=result["grade"],
        quality_score=result["score"],
        record_id=record.id,
        input_parameters=features,
    )


@router.get("/history/{cow_id}", response_model=List[MilkRecordResponse])
def get_milk_history(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    return db.query(MilkRecord).filter(MilkRecord.cow_id == cow_id).order_by(MilkRecord.created_at.desc()).all()
