from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.api.routers import api_router
from app.api.routers.health import router as health_router
from app.api.error_handlers import register_error_handlers
from app.core.logging import configure_logging
from app.core.rate_limiter import RateLimiterMiddleware
from app.db.session import init_db
from app.core.seed import seed_default_data

app = FastAPI(title="Administrator Panel Backend System", version="1.0")

configure_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=RateLimiterMiddleware(max_requests_per_minute=100))

register_error_handlers(app)

@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_default_data()

app.include_router(health_router, tags=["Health"])
app.include_router(api_router, prefix="/api")