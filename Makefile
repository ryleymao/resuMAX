# ResuMAX Makefile
# Cross-platform development automation

.PHONY: help up down logs test-backend test-frontend lint migrate build clean

help:
	@echo "ResuMAX Development Commands:"
	@echo "  make up             Start backend, frontend, and database (Docker)"
	@echo "  make down           Stop all containers"
	@echo "  make logs           View logs"
	@echo "  make test-backend   Run backend tests"
	@echo "  make test-frontend  Run frontend tests"
	@echo "  make lint           Run linters"
	@echo "  make migrate        Run database migrations"
	@echo "  make build          Build production images"
	@echo "  make clean          Remove temporary files"

# Docker Development
up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

# Testing
test-backend:
	docker-compose exec backend pytest

test-frontend:
	docker-compose exec frontend npm test

# Linting
lint:
	docker-compose exec backend flake8 app
	docker-compose exec frontend npm run lint

# Database
migrate:
	docker-compose exec backend python -m app.db.migrations

# Build
build:
	docker-compose build

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	rm -rf backend/uploads/* backend/temp/*
