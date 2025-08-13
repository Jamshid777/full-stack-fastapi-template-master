from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.payment import Payment
from app.db.models.user_payout import UserPayout
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.security import get_password_hash
from app.api.deps import require_roles

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=dict)
def list_users(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("admin", "moderator")),
):
    query = db.query(User)
    if search:
        like = f"%{search}%"
        query = query.filter(func.lower(User.full_name).like(func.lower(like)))
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * size).limit(size).all()
    return {"items": [UserOut.model_validate(u) for u in items], "total": total, "page": page, "size": size}

@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    exists = db.query(User).filter(User.phone == payload.phone).first()
    if exists:
        raise HTTPException(status_code=400, detail="Phone already exists")
    user = User(
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        address=payload.address,
        role=payload.role,
        share_percentage=payload.share_percentage,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "password" and value:
            setattr(user, "password_hash", get_password_hash(value))
        elif field != "password":
            setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return

@router.get("/balances", response_model=dict)
def user_balances(db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    users = db.query(User).all()
    result = []
    for u in users:
        total_earnings = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()  # Simplified: overall earnings
        total_payouts = db.query(func.coalesce(func.sum(UserPayout.amount), 0)).filter(UserPayout.user_id == u.id).scalar() or 0
        current_balance = float(total_earnings) * float(u.share_percentage) / 100 - float(total_payouts)
        result.append({
            "id": u.id,
            "full_name": u.full_name,
            "share_percentage": float(u.share_percentage),
            "total_earnings": float(total_earnings),
            "total_payouts": float(total_payouts),
            "current_balance": float(current_balance),
        })
    return {"users": result}