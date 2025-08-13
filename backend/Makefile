run:
	uvicorn app.main:app --reload --port 8000

dev-db:
	docker compose up -d db

migrate:
	alembic revision --autogenerate -m "auto"
	alembic upgrade head