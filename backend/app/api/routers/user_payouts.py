from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user_payout import UserPayout
from app.schemas.user_payout import UserPayoutCreate, UserPayoutOut
from app.api.deps import require_roles

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=dict)
def list_payouts(
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("admin", "moderator")),
):
    query = db.query(UserPayout)
    if user_id:
        query = query.filter(UserPayout.user_id == user_id)
    if start_date:
        query = query.filter(UserPayout.payout_date >= start_date)
    if end_date:
        query = query.filter(UserPayout.payout_date <= end_date)
    total = query.count()
    items = query.order_by(UserPayout.payout_date.desc()).offset((page - 1) * size).limit(size).all()
    return {"items": [UserPayoutOut.model_validate(i) for i in items], "total": total, "page": page, "size": size}

@router.post("", response_model=UserPayoutOut, status_code=201)
def create_payout(payload: UserPayoutCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    payout = UserPayout(**payload.model_dump())
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return UserPayoutOut.model_validate(payout)

@router.delete("/{payout_id}", status_code=204)
def delete_payout(payout_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    payout = db.get(UserPayout, payout_id)
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    db.delete(payout)
    db.commit()
    return