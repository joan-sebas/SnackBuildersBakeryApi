.PHONY: help install up down logs build test test-unit test-integration test-cov lint format type-check migrate seed clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install --upgrade pip setuptools wheel
	pip install -e ".[dev]"
	pre-commit install

up: ## Start the full stack with docker compose
	docker compose up --build

down: ## Stop the stack
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

build: ## Rebuild docker images
	docker compose build

test: ## Run all tests with coverage
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit -m "not integration and not concurrency"

test-integration: ## Run integration tests
	pytest tests/integration -m integration

test-concurrency: ## Run concurrency tests
	pytest tests/concurrency -m concurrency

test-cov: ## Run tests and open the coverage report
	pytest --cov-report=html
	@echo "Coverage report at htmlcov/index.html"

lint: ## Run ruff and mypy
	ruff check src tests
	ruff format --check src tests
	mypy src

format: ## Format code with ruff
	ruff format src tests
	ruff check --fix src tests

type-check: ## Run mypy only
	mypy src

migrate: ## Apply database migrations
	alembic upgrade head

migrate-revision: ## Create a new migration (usage: make migrate-revision MSG="description")
	alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed the database with menu and customers
	python -m scripts.seed_menu
	python -m scripts.seed_customers

clean: ## Remove build artifacts and caches
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
