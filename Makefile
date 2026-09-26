.PHONY: help install install-dev test test-frontend lint format run deploy clean

help:
	@echo "QFZZ FuzzyRadio - Development Commands"
	@echo ""
	@echo "  make install        Install dependencies"
	@echo "  make install-dev    Install dev dependencies"
	@echo "  make test           Run pytest"
	@echo "  make test-frontend  Run frontend Vitest"
	@echo "  make lint           Run linting"
	@echo "  make format         Format code"
	@echo "  make run            Start server"
	@echo "  make deploy         Deploy to Firebase"
	@echo "  make clean          Clean build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=qfzz --cov-report=html --cov-report=term

test-frontend:
	cd frontend && npm test

lint:
	ruff check qfzz/ tests/

format:
	ruff format qfzz/ tests/
	isort qfzz/ tests/

run:
	python run_server.py

deploy:
	firebase deploy --only hosting

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
