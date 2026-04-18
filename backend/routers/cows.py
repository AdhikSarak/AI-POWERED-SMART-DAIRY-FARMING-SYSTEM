from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.cow import Cow
from backend.schemas.cow import CowCreate, CowUpdate, CowResponse
from backend.core.dependencies import get_current_farmer
from backend.models.user import User
import uuid

router = APIRouter()


def generate_cow_uid():
    return f"COW-{str(uuid.uuid4())[:8].upper()}"


@router.post("/", response_model=CowResponse, status_code=201)
def add_cow(payload: CowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow_uid = payload.cow_uid or generate_cow_uid()
    existing = db.query(Cow).filter(Cow.cow_uid == cow_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cow UID already exists")

    cow = Cow(
        cow_uid=cow_uid,
        name=payload.name,
        age=payload.age,
        breed=payload.breed,
        weight_kg=payload.weight_kg,
        farmer_id=current_user.id,
    )
    db.add(cow)
    db.commit()
    db.refresh(cow)
    return cow


@router.get("/", response_model=List[CowResponse])
def list_cows(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    if current_user.role == "admin":
        return db.query(Cow).all()
    return db.query(Cow).filter(Cow.farmer_id == current_user.id).all()


@router.get("/{cow_id}", response_model=CowResponse)
def get_cow(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    if current_user.role != "admin" and cow.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your cow")
    return cow


@router.put("/{cow_id}", response_model=CowResponse)
def update_cow(cow_id: int, payload: CowUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cow, field, value)
    db.commit()
    db.refresh(cow)
    return cow


@router.delete("/{cow_id}", status_code=204)
def delete_cow(cow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    cow = db.query(Cow).filter(Cow.id == cow_id, Cow.farmer_id == current_user.id).first()
    if not cow:
        raise HTTPException(status_code=404, detail="Cow not found")
    db.delete(cow)
    db.commit()
