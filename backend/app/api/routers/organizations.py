from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import uuid4
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.db.models.branch import Branch
from app.db.models.device import Device
from app.db.models.add_on import AddOn
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationOut,
    OrganizationListResponse,
    BranchCreate,
    BranchOut,
    DeviceCreate,
    DeviceOut,
    AddOnCreate,
    AddOnOut,
    LoginResponse,
    LoginRequest,
)
from app.api.deps import require_roles
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=OrganizationListResponse)
def list_organizations(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    plan: Optional[str] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("admin", "moderator", "registrator")),
):
    query = db.query(Organization)
    if search:
        like = f"%{search}%"
        query = query.filter(func.lower(Organization.name).like(func.lower(like)))
    if plan:
        query = query.filter(Organization.plan == plan)
    total = query.count()
    items = query.order_by(Organization.id.desc()).offset((page - 1) * size).limit(size).all()
    return OrganizationListResponse(items=[OrganizationOut.model_validate(i) for i in items], total=total, page=page, size=size)

@router.post("", response_model=OrganizationOut, status_code=201)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator"))):
    existing_org = db.query(Organization).filter(Organization.phone == payload.phone).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization with this phone number already exists")
    org_data = payload.model_dump()
    password = org_data.pop("password")
    org = Organization(**org_data, password_hash=get_password_hash(password))
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrganizationOut.model_validate(org)

@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: int, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(require_roles("admin", "moderator", "registrator", "organization")),
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if payload.get("role") == "registrator" and org.registrator_id != int(payload.get("sub")):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    org_out = OrganizationOut.model_validate(org)
    if payload.get("role") == "admin":
        org_out.password = org.password_hash
    return org_out


@router.get("/phone/{phone}", response_model=OrganizationOut)
def get_organization_by_phone_number(
    phone: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_roles("admin", "moderator", "registrator", "organization")),
):
    org = db.query(Organization).filter(Organization.phone == phone).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if payload.get("role") == "registrator" and org.registrator_id != int(
        payload.get("sub")
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    org_out = OrganizationOut.model_validate(org)
    if payload.get("role") == "admin":
        org_out.password = org.password_hash
    return org_out

@router.put("/{org_id}", response_model=OrganizationOut)
def update_organization(org_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    update_data = payload.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        org.password_hash = get_password_hash(update_data.pop("password"))
    for k, v in update_data.items():
        setattr(org, k, v)
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrganizationOut.model_validate(org)

@router.delete("/{org_id}", status_code=204)
def delete_organization(org_id: int, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin"))):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(org)
    db.commit()
    return

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.phone == payload.phone).first()

    if not org or not verify_password(payload.password, org.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect phone or password",
        )
    access_token = create_access_token(str(org.id), {"role": "organization"})
    refresh_token = create_refresh_token(str(org.id))
    return LoginResponse(
        access_token=access_token, 
        refresh_token=refresh_token, 
        user=OrganizationOut.model_validate(org)
    )

@router.get("/{org_id}/branches", response_model=list[BranchOut])
def list_branches(
    org_id: int, 
    db: Session = Depends(get_db),
    payload: dict = Depends(require_roles("admin", "moderator", "registrator", "organization")),
):
    if payload.get("role") == "registrator":
        org = db.get(Organization, org_id)
        if not org or org.registrator_id != int(payload.get("sub")):
            raise HTTPException(status_code=403, detail="Forbidden")
    q = db.query(Branch).filter(Branch.organization_id == org_id)
    branches = q.all()
    return [BranchOut.model_validate(b) for b in branches]

@router.post("/{org_id}/branches", response_model=BranchOut, status_code=201)
def create_branch(org_id: int, payload: BranchCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    existing_branch = db.query(Branch).filter(
        Branch.organization_id == org_id,
        Branch.name == payload.name,
        Branch.location == payload.location
    ).first()
    if existing_branch:
        raise HTTPException(status_code=400, detail="Branch with this name and location already exists in this organization")
    branch = Branch(organization_id=org_id, **payload.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return BranchOut.model_validate(branch)

@router.get("/{org_id}/devices", response_model=list[DeviceOut])
def list_devices(
    org_id: int, 
    db: Session = Depends(get_db),
    payload: dict = Depends(require_roles("admin", "moderator", "registrator", "organization")),
    ):
    if payload.get("role") == "registrator":
        org = db.get(Organization, org_id)
        if not org or org.registrator_id != int(payload.get("sub")):
            raise HTTPException(status_code=403, detail="Forbidden")
    devices = (
        db.query(Device)
        .join(Branch, Device.branch_id == Branch.id)
        .filter(Branch.organization_id == org_id)
        .all()
    )
    return [DeviceOut.model_validate(d) for d in devices]

@router.post("/{org_id}/devices", response_model=DeviceOut, status_code=201)
def create_device(org_id: int, payload: DeviceCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    branch = db.get(Branch, payload.branch_id)
    if not branch or branch.organization_id != org_id:
        raise HTTPException(status_code=400, detail="Invalid branch")
        
    existing_device = db.query(Device).filter(
        Device.branch_id == payload.branch_id,
        Device.name == payload.name,
        Device.os == payload.os
    ).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Device with this name and OS already exists in this branch")
    
    device = Device(id=str(uuid4()), branch_id=payload.branch_id, name=payload.name, os=payload.os)
    db.add(device)
    db.commit()
    db.refresh(device)
    return DeviceOut.model_validate(device)

@router.put("/{org_id}/devices/{device_id}", response_model=DeviceOut)
def update_device(org_id: int, device_id: str, payload: DeviceCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    branch = db.get(Branch, payload.branch_id)
    if not branch or branch.organization_id != org_id:
        raise HTTPException(status_code=400, detail="Invalid branch")
    device.branch_id = payload.branch_id
    device.name = payload.name
    device.os = payload.os
    db.add(device)
    db.commit()
    db.refresh(device)
    return DeviceOut.model_validate(device)

@router.delete("/{org_id}/devices/{device_id}", status_code=204)
def delete_device(org_id: int, device_id: str, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    # ensure belongs to org
    branch = db.get(Branch, device.branch_id)
    if not branch or branch.organization_id != org_id:
        raise HTTPException(status_code=400, detail="Invalid organization")
    db.delete(device)
    db.commit()
    return

@router.get("/{org_id}/add-ons", response_model=list[AddOnOut])
def list_addons(
    org_id: int, 
    db: Session = Depends(get_db),
    payload: dict = Depends(require_roles("admin", "moderator", "registrator", "organization")),
    ):
    if payload.get("role") == "registrator":
        org = db.get(Organization, org_id)
        if not org or org.registrator_id != int(payload.get("sub")):
            raise HTTPException(status_code=403, detail="Forbidden")
    addons = db.query(AddOn).filter(AddOn.organization_id == org_id).all()
    return [AddOnOut.model_validate(a) for a in addons]

@router.post("/{org_id}/add-ons", response_model=AddOnOut, status_code=201)
def create_addon(org_id: int, payload: AddOnCreate, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    addon = AddOn(id=str(uuid4()), organization_id=org_id, **payload.model_dump())
    db.add(addon)
    db.commit()
    db.refresh(addon)
    return AddOnOut.model_validate(addon)

@router.delete("/{org_id}/add-ons/{addon_id}", status_code=204)
def delete_addon(org_id: int, addon_id: str, db: Session = Depends(get_db), _: dict = Depends(require_roles("admin", "moderator", "organization"))):
    addon = db.get(AddOn, addon_id)
    if not addon or addon.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Add-on not found")
    db.delete(addon)
    db.commit()
    return