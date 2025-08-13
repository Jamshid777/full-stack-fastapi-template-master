from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.session import SessionLocal
from app.db.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentListResponse, SverkaResponse
from app.api.deps import require_roles

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=PaymentListResponse)
def list_payments(
    organization_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("admin", "moderator")),
):
    query = db.query(Payment)
    if organization_id:
        query = query.filter(Payment.organization_id == organization_id)
    if start_date and end_date:
        query = query.filter(and_(Payment.payment_date >= start_date, Payment.payment_date <= end_date))
    if source:
        query = query.filter(Payment.source == source)
    total = query.count()
    items = query.order_by(Payment.payment_date.desc()).offset((page - 1) * size).limit(size).all()
    return PaymentListResponse(items=[PaymentOut.model_validate(i) for i in items], total=total, page=page, size=size)

@router.post("", response_model=PaymentOut, status_code=201)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    payment = Payment(**payload.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return PaymentOut.model_validate(payment)

@router.get("/sverka/{organization_id}", response_model=SverkaResponse)
def sverka(organization_id: int, start_date: date, end_date: date, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    total = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.organization_id == organization_id)
        .filter(Payment.payment_date >= start_date)
        .filter(Payment.payment_date <= end_date)
        .scalar()
    )
    return SverkaResponse(organization_id=organization_id, start_date=start_date, end_date=end_date, total_amount=float(total))