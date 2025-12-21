.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	cd frontend && npm install

dev: ## Run development servers
	@echo "Starting backend and frontend..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	cd frontend && npm run dev

test: ## Run tests
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch tests/ -v

lint: ## Run linting
	black --check app tests
	flake8 app tests --max-line-length=120
	mypy app --ignore-missing-imports
	cd frontend && npm run lint

format: ## Format code
	black app tests
	isort app tests
	cd frontend && npm run format

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov .coverage coverage.xml
	rm -rf frontend/.next frontend/out frontend/node_modules/.cache

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-restart: ## Restart Docker containers
	docker-compose restart

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down: ## Rollback last migration
	alembic downgrade -1

setup: ## Initial project setup
	@echo "Setting up project..."
	pip install -r requirements.txt
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make migrate && make docker-up"

db-shell: ## Open database shell
	docker-compose exec postgres psql -U postgres -d ai_code_review

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

backend-shell: ## Open backend container shell
	docker-compose exec backend bash

pre-commit-install: ## Install pre-commit hooks
	pip install pre-commit
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

coverage: ## Generate coverage report
	pytest tests/ --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

security-check: ## Run security checks
	pip install bandit safety
	bandit -r app/
	safety check

deploy-prod: ## Deploy to production
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.prod.yml up -d
	docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

init-db: ## Initialize database with seed data
	python -m app.scripts.init_database
	python -m app.scripts.init_knowledge_base
