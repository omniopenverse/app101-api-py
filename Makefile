SHELL := /bin/bash
.DEFAULT_GOAL := help

# Project variables (override via environment if needed)
PY := python3
PIP := $(PY) -m pip
VENV_DIR := .venv
REQ := requirements.txt
REQ_DEV := requirements-dev.txt

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create local virtual environment at $(VENV_DIR)
	@$(PY) -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/python -m pip install --upgrade pip setuptools wheel >/dev/null

pre-install: venv ## Install minimal tooling from $(REQ_DEV) into venv
	$(VENV_DIR)/bin/pip install -r $(REQ_DEV)

install: venv ## Install prod dependencies from $(REQ) into venv
	@$(VENV_DIR)/bin/pip install -r $(REQ)

test: ## Run pytest
	@$(VENV_DIR)/bin/python -m pytest -q

coverage: ## Run coverage with terminal report
	@$(VENV_DIR)/bin/python -m coverage run -m pytest
	@$(VENV_DIR)/bin/python -m coverage report -m

coverage-html: ## Generate HTML coverage report in htmlcov/index.html
	@$(VENV_DIR)/bin/python -m coverage run -m pytest
	@$(VENV_DIR)/bin/python -m coverage html
	@echo "HTML coverage report generated at htmlcov/index.html"

lint: ## Lint code with ruff
	@$(VENV_DIR)/bin/python -m ruff check src tests

format: ## Format code with black and fix lint with ruff
	@$(VENV_DIR)/bin/python -m black src tests
	@$(VENV_DIR)/bin/python -m ruff check --fix src tests || true

typecheck: ## Type-check with mypy
	@$(VENV_DIR)/bin/python -m mypy src

pip-audit: ## Run pip-audit on production requirements
	@echo "[pip-audit] Running pip-audit (advisory DB)"
	@$(VENV_DIR)/bin/python -m pip_audit -r $(REQ) || true

pip-adev: ## Run pip-audit on development requirements
	@$(VENV_DIR)/bin/python -m pip_audit -r $(REQ_DEV) || true

safety: ## Run safety check on installed packages
	@echo "[safety] Running safety (vuln DB)"
	@$(VENV_DIR)/bin/python -m safety check --full-report || true

bandit: ## Run bandit static analysis on source code
	@echo "[bandit] Running bandit (static analysis)"
	@$(VENV_DIR)/bin/python -m bandit -r src || true

package:
	@cp -r src dist/
	@find dist/ -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf dist/db.sqlite3 || true

sci: pip-audit safety bandit ## Security checks: dependencies & code (pip-audit, safety, bandit)

# ci: pre-install install lint test coverage sci ## Run lint, test, coverage and sci (for CI pipelines)
ci: pre-install install test coverage sci ## Run test, coverage and sci (for CI pipelines)

run: ## Run local app (env: APP_ENV=local)
	@mkdir -p local
	@APP101_LOG_FILE=local/app.log APP_ENV=local \
		$(VENV_DIR)/bin/python src/app.py

docker-build: ## Build Docker images
	@docker compose build

docker-up: ## Start services with docker compose
	@docker compose up -d

docker-down: ## Stop services and remove volumes
	@docker compose down -v

docker-logs: ## Tail docker compose logs
	@docker compose logs -f --tail=200

clean: ## Remove caches, coverage, local DB
	rm -rf htmlcov .pytest_cache local src/db.sqlite3 .coverage .mypy_cache .ruff_cache dist
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean ## Clean + remove venv
	rm -rf .venv

.PHONY: help \
		venv pre-install install \
		test coverage coverage-html \
		lint format typecheck \
		pip-audit pip-adev safety bandit sci \
		ci \
		run \
		docker-build docker-up docker-down docker-logs \
		clean fclean