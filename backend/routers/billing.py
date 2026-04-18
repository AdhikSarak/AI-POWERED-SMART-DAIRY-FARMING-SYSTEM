from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.milk_collection import MilkCollection
from backend.models.billing import Billing
from backend.schemas.billing import MilkCollectionCreate, MilkCollectionResponse, BillingResponse, GenerateBillRequest
from backend.core.dependencies import get_current_admin, get_current_farmer
from backend.services.billing_service import calculate_bill
from backend.services.pdf_service import generate_bill_pdf
from backend.models.user import User

router = APIRouter()


@router.post("/collection", response_model=MilkCollectionResponse, status_code=201)
def record_collection(
    payload: MilkCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    record = MilkCollection(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/collection", response_model=List[MilkCollectionResponse])
def list_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(MilkCollection).order_by(MilkCollection.collection_date.desc()).all()


@router.get("/collection/farmer/{farmer_id}", response_model=List[MilkCollectionResponse])
def farmer_collections(farmer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    return db.query(MilkCollection).filter(MilkCollection.farmer_id == farmer_id).order_by(MilkCollection.collection_date.desc()).all()


@router.post("/generate-bill", response_model=BillingResponse)
def generate_bill(
    payload: GenerateBillRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = calculate_bill(db, payload.farmer_id, payload.month)
    if not result:
        raise HTTPException(status_code=404, detail="No milk collections found for this month")

    farmer = db.query(User).filter(User.id == payload.farmer_id).first()
    pdf_path = generate_bill_pdf(farmer, result, payload.month)

    bill = Billing(
        farmer_id=payload.farmer_id,
        month=payload.month,
        total_liters=result["total_liters"],
        total_amount=result["total_amount"],
        bill_pdf_path=pdf_path,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


@router.get("/bills", response_model=List[BillingResponse])
def list_bills(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Billing).order_by(Billing.created_at.desc()).all()


@router.get("/bills/farmer/{farmer_id}", response_model=List[BillingResponse])
def farmer_bills(farmer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    return db.query(Billing).filter(Billing.farmer_id == farmer_id).order_by(Billing.created_at.desc()).all()
