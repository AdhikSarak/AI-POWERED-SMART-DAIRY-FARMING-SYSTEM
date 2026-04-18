from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os, shutil, uuid
from backend.database import get_db
from backend.models.cow import Cow
from backend.models.health_record import HealthRecord
from backend.schemas.health import HealthRecordResponse, HealthAnalysisResult
from backend.core.dependencies import get_current_farmer
from backend.core.config import settings
from backend.services.disease_service import predict_disease
from backend.models.user import User

router = APIRouter()


@router.post("/analyze", response_model=HealthAnalysisResult)
async def analyze_health(
    cow_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_farmer),
):
    cow = db.query(Cow).filter(Cow.id == cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    # Save uploaded image
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[-1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run disease detection
    result = predict_disease(file_path)

    # Save to DB
    record = HealthRecord(
        cow_id=cow_id,
        image_path=file_path,
        disease_name=result["disease"],
        confidence_score=result["confidence"],
        health_status=result["status"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return HealthAnalysisResult(
        cow_id=cow_id,
        disease_name=result["disease"],
        confidence_score=result["confidence"],
        health_status=result["status"],
        all_predictions=result["all_predictions"],
        record_id=record.id,
    )


@router.get("/history/{cow_id}", response_model=List[HealthRecordResponse])
def get_health_history(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    return db.query(HealthRecord).filter(HealthRecord.cow_id == cow_id).order_by(HealthRecord.created_at.desc()).all()
