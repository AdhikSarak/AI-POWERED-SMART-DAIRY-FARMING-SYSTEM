from sqlalchemy.orm import Session
from backend.models.milk_collection import MilkCollection


def calculate_bill(db: Session, farmer_id: int, month: str) -> dict:
    """Calculate total bill for a farmer for a given month (e.g. '2024-04')."""
    year, mon = month.split("-")

    collections = db.query(MilkCollection).filter(
        MilkCollection.farmer_id == farmer_id,
    ).all()

    # Filter by month
    month_collections = [
        c for c in collections
        if str(c.collection_date.year) == year and str(c.collection_date.month).zfill(2) == mon
    ]

    if not month_collections:
        return None

    total_liters = sum(c.quantity_liters for c in month_collections)
    total_amount = sum(c.quantity_liters * c.rate_per_liter for c in month_collections)

    breakdown = [
        {
            "date": str(c.collection_date),
            "liters": c.quantity_liters,
            "quality": c.quality_grade,
            "rate": c.rate_per_liter,
            "amount": round(c.quantity_liters * c.rate_per_liter, 2),
        }
        for c in month_collections
    ]

    return {
        "total_liters": round(total_liters, 2),
        "total_amount": round(total_amount, 2),
        "breakdown":    breakdown,
        "record_count": len(month_collections),
    }
