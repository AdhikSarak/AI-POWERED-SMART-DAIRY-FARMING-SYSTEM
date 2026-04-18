from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.cow import Cow
from backend.models.health_record import HealthRecord
from backend.models.milk_record import MilkRecord
from backend.models.recommendation import Recommendation
from backend.core.dependencies import get_current_farmer
from backend.models.user import User

router = APIRouter()


@router.get("/cow/{cow_id}")
def cow_full_report(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")

    health  = db.query(HealthRecord).filter(HealthRecord.cow_id == cow_id).order_by(HealthRecord.created_at.desc()).all()
    milk    = db.query(MilkRecord).filter(MilkRecord.cow_id == cow_id).order_by(MilkRecord.created_at.desc()).all()
    recs    = db.query(Recommendation).filter(Recommendation.cow_id == cow_id).order_by(Recommendation.created_at.desc()).all()

    return {
        "cow": {"id": cow.id, "cow_uid": cow.cow_uid, "name": cow.name, "age": cow.age, "breed": cow.breed},
        "health_records": [{"disease": h.disease_name, "confidence": h.confidence_score, "status": h.health_status, "date": str(h.created_at)} for h in health],
        "milk_records":   [{"grade": m.quality_grade, "score": m.quality_score, "ph": m.ph, "fat": m.fat, "date": str(m.created_at)} for m in milk],
        "recommendations":[{"type": r.rec_type, "content": r.content, "date": str(r.created_at)} for r in recs],
    }


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    if current_user.role == "admin":
        total_cows    = db.query(Cow).count()
        total_farmers = db.query(User).filter(User.role == "farmer").count()
    else:
        total_cows    = db.query(Cow).filter(Cow.farmer_id == current_user.id).count()
        total_farmers = 1

    total_health = db.query(HealthRecord).count()
    total_milk   = db.query(MilkRecord).count()

    recent_health = db.query(HealthRecord).order_by(HealthRecord.created_at.desc()).limit(5).all()
    recent_milk   = db.query(MilkRecord).order_by(MilkRecord.created_at.desc()).limit(5).all()

    diseased_count    = db.query(HealthRecord).filter(HealthRecord.health_status == "Diseased").count()
    good_milk_count    = db.query(MilkRecord).filter(MilkRecord.quality_grade == "Good").count()
    average_milk_count = db.query(MilkRecord).filter(MilkRecord.quality_grade == "Average").count()
    poor_milk_count    = db.query(MilkRecord).filter(MilkRecord.quality_grade == "Poor").count()

    return {
        "total_cows":          total_cows,
        "total_farmers":       total_farmers,
        "total_health_checks": total_health,
        "total_milk_tests":    total_milk,
        "diseased_count":      diseased_count,
        "good_milk_count":     good_milk_count,
        "average_milk_count":  average_milk_count,
        "poor_milk_count":     poor_milk_count,
        "recent_health": [
            {"cow_id": h.cow_id, "disease": h.disease_name, "status": h.health_status, "date": str(h.created_at.date())}
            for h in recent_health
        ],
        "recent_milk": [
            {"cow_id": m.cow_id, "grade": m.quality_grade, "score": m.quality_score, "date": str(m.created_at.date())}
            for m in recent_milk
        ],
    }
