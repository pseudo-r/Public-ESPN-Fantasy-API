help:
	@echo "ESPN Fantasy API Service — available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make migrate      Run database migrations"
	@echo "  make run          Start dev server (port 8001)"
	@echo "  make worker       Start Celery worker"
	@echo "  make up           Start all Docker services"
	@echo "  make down         Stop all Docker services"
	@echo "  make shell        Django shell"
	@echo "  make test         Run test suite"
	@echo "  make lint         Run ruff linter"
	@echo "  make sync         Sync a league (requires GAME, SEASON, LEAGUE env vars)"

install:
	pip install -e ".[dev]"

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8001

worker:
	celery -A config worker --loglevel=info --concurrency=2

up:
	docker compose up --build -d

down:
	docker compose down

shell:
	python manage.py shell

test:
	pytest

lint:
	ruff check . && ruff format --check .

sync:
	python manage.py sync_fantasy \
		--game $(or $(GAME),ffl) \
		--season $(or $(SEASON),2025) \
		--league $(LEAGUE)

.PHONY: help install migrate run worker up down shell test lint sync
