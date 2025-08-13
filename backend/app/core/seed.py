from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.plan import CustomPlan
from app.core.security import get_password_hash


def seed_default_data() -> None:
    db: Session = SessionLocal()
    try:
        # Seed admin user
        admin = db.execute(select(User).where(User.phone == "admin")).scalar_one_or_none()
        if admin is None:
            admin_user = User(
                full_name="Admin User",
                phone="admin",
                password_hash=get_password_hash("admin123"),
                role="admin",
                share_percentage=0.0,
            )
            db.add(admin_user)
        # Seed default plans if none
        has_plans = db.execute(select(CustomPlan).limit(1)).scalar_one_or_none()
        if has_plans is None:
            plans = [
                CustomPlan(
                    name="Free",
                    branches=1,
                    devices_per_branch=2,
                    waiters=0,
                    kds=False,
                    warehouse_control="none",
                    tech_card="none",
                    chat_support=False,
                    api_integrations=[],
                    phone_support_247=False,
                    personal_manager=False,
                    monthly_price=0,
                    yearly_price=0,
                    flag="Hamyonbop",
                    color="#6c757d",
                ),
                CustomPlan(
                    name="Basic",
                    branches=5,
                    devices_per_branch=10,
                    waiters=5,
                    kds=True,
                    warehouse_control="lite",
                    tech_card="lite",
                    chat_support=True,
                    api_integrations=["Uzum tezkor"],
                    phone_support_247=False,
                    personal_manager=False,
                    monthly_price=150000,
                    yearly_price=1500000,
                    flag="Ommabop",
                    color="#007bff",
                ),
                CustomPlan(
                    name="Premium",
                    branches=100,
                    devices_per_branch=100,
                    waiters=100,
                    kds=True,
                    warehouse_control="pro",
                    tech_card="pro",
                    chat_support=True,
                    api_integrations=["Uzum tezkor", "Yandex delivery", "Wolt"],
                    phone_support_247=True,
                    personal_manager=True,
                    monthly_price=400000,
                    yearly_price=4000000,
                    flag="Premium",
                    color="#6a1b9a",
                ),
            ]
            db.add_all(plans)
        db.commit()
    finally:
        db.close()