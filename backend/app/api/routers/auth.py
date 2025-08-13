from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.registration_request import RegistrationRequest
from app.schemas.user import LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse, UserOut
from app.schemas.registration_request import RegistrationRequestCreate
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone, User.is_active == True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(str(user.id), {"role": user.role})
    refresh = create_refresh_token(str(user.id))
    return LoginResponse(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))

@router.post("/register-request", status_code=201)
def register_request(payload: RegistrationRequestCreate, db: Session = Depends(get_db)):
    req = RegistrationRequest(full_name=payload.full_name, phone=payload.phone, password=payload.password, address=payload.address)
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": req.id, "status": req.status}

@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(payload: TokenRefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = decoded.get("sub")
        access = create_access_token(user_id)
        return TokenRefreshResponse(access_token=access)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")