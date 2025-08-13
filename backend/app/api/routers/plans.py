from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.plan import CustomPlan
from app.schemas.plan import PlanCreate, PlanUpdate, PlanOut
from app.api.deps import require_roles

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    items = db.query(CustomPlan).filter(CustomPlan.is_active == True).order_by(CustomPlan.id.asc()).all()
    return [PlanOut.model_validate(i) for i in items]

@router.post("", response_model=PlanOut, status_code=201)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    plan = CustomPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanOut.model_validate(plan)

@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(CustomPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanOut.model_validate(plan)

@router.put("/{plan_id}", response_model=PlanOut)
def update_plan(plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    plan = db.get(CustomPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanOut.model_validate(plan)

@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    plan = db.get(CustomPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return