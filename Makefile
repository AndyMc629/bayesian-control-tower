.DEFAULT_GOAL := help

.PHONY: help install install-dev test lint typecheck format run build-image dev clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

install-dev: ## Install all dependencies including dev
	uv sync

hooks: ## Install pre-commit hooks into the local git repo
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

test: ## Run test suite with coverage
	uv run pytest

test-watch: ## Run tests in watch mode (requires pytest-watch)
	uv run ptw

lint: ## Lint with ruff
	uv run ruff check src tests

format: ## Format with ruff
	uv run ruff format src tests

typecheck: ## Run mypy
	uv run mypy src

check: lint typecheck test ## Run all checks

run: ## Run the A2A server locally
	uv run serve

dev: ## Run with auto-reload
	uv run uvicorn bayesian_control_tower.server:app --reload --host 0.0.0.0 --port 8000

build-image: ## Build the Docker image
	docker build -t bayesian-control-tower:local .

run-image: ## Run the Docker image
	docker run --env-file .env -p 8000:8000 bayesian-control-tower:local

clean: ## Remove build artifacts and caches
	rm -rf .venv dist .mypy_cache .ruff_cache .pytest_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
