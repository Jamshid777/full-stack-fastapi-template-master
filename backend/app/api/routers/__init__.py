from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .organizations import router as orgs_router
from .payments import router as payments_router
from .user_payouts import router as payouts_router
from .plans import router as plans_router
from .registration_requests import router as regreq_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(orgs_router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(payouts_router, prefix="/user-payouts", tags=["User Payouts"])
api_router.include_router(plans_router, prefix="/plans", tags=["Plans"])
api_router.include_router(regreq_router, prefix="/registration-requests", tags=["Registration Requests"])