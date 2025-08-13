# Administrator Panel Backend System

Quick start:

- Local: `cp .env.example .env && docker compose up --build`
- Alembic: `alembic revision --autogenerate -m "init" && alembic upgrade head`
- Dev server: `uvicorn app.main:app --reload`

Docs: `/docs` and `/redoc`.