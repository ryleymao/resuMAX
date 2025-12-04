.PHONY: help dev test lint format migrate clean docker-up docker-down

help:
	@echo "ResuMAX Backend - Available Commands:"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make migrate      - Run database migrations"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch:
	pytest-watch tests/ -v

lint:
	@echo "Running flake8..."
	flake8 app tests
	@echo "Running mypy..."
	mypy app
	@echo "Running isort check..."
	isort app tests --check-only
	@echo "Running black check..."
	black app tests --check

format:
	@echo "Formatting with black..."
	black app tests
	@echo "Sorting imports with isort..."
	isort app tests

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose up -d --build

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt

db-init:
	python -m app.core.database

celery-worker:
	celery -A app.worker worker --loglevel=info

celery-flower:
	celery -A app.worker flower --port=5555
