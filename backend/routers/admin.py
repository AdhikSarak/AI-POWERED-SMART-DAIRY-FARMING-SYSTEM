from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.user import User
from backend.models.cow import Cow
from backend.models.health_record import HealthRecord
from backend.models.milk_record import MilkRecord
from backend.models.milk_collection import MilkCollection
from backend.models.billing import Billing
from backend.schemas.user import UserResponse
from backend.core.dependencies import get_current_admin

router = APIRouter()


@router.get("/farmers", response_model=List[UserResponse])
def list_farmers(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(User).filter(User.role == "farmer").all()


@router.get("/stats")
def system_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return {
        "total_farmers":     db.query(User).filter(User.role == "farmer").count(),
        "total_cows":        db.query(Cow).count(),
        "total_health_checks": db.query(HealthRecord).count(),
        "total_milk_tests":  db.query(MilkRecord).count(),
        "total_collections": db.query(MilkCollection).count(),
        "total_bills":       db.query(Billing).count(),
    }


@router.delete("/farmer/{farmer_id}", status_code=204)
def delete_farmer(farmer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == farmer_id, User.role == "farmer").first()
    if not user:
        raise HTTPException(status_code=404, detail="Farmer not found")
    db.delete(user)
    db.commit()
