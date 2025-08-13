from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    # Import models to ensure they are registered with Base.metadata
    from app.db.models import all_models  # noqa: F401
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)