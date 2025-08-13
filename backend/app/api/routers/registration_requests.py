from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.registration_request import RegistrationRequest
from app.db.models.user import User
from app.schemas.registration_request import RegistrationApprovePayload
from app.core.security import get_password_hash
from app.api.deps import require_roles

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[dict])
def list_requests(db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    items = db.query(RegistrationRequest).order_by(RegistrationRequest.id.desc()).all()
    return [
        {
            "id": r.id,
            "full_name": r.full_name,
            "phone": r.phone,
            "address": r.address,
            "status": r.status,
        }
        for r in items
    ]

@router.post("/{req_id}/approve")
def approve(req_id: int, payload: RegistrationApprovePayload, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    req = db.get(RegistrationRequest, req_id)
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found or not pending")
    user = User(
        full_name=req.full_name,
        phone=req.phone,
        password_hash=get_password_hash(req.password),
        address=req.address,
        role="registrator",
        share_percentage=payload.share_percentage,
    )
    db.add(user)
    req.status = "approved"
    db.commit()
    return {"status": "approved"}

@router.post("/{req_id}/reject")
def reject(req_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    req = db.get(RegistrationRequest, req_id)
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="Request not found or not pending")
    req.status = "rejected"
    db.add(req)
    db.commit()
    return {"status": "rejected"}