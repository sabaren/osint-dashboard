.PHONY: up down test format lint clean backup

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f web worker

test:
	pytest tests/ -v --tb=short

format:
	black app/ tests/

lint:
	ruff check app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

backup:
	python -m app.scripts.backup

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A app.celery_app.celery_app worker --loglevel=info

beat:
	celery -A app.celery_app.celery_app beat --loglevel=info
