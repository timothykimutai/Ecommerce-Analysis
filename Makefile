.PHONY: help install test lint format clean run-etl run-analysis docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Remove generated files"
	@echo "  make run-etl       - Run data cleaning pipeline"
	@echo "  make run-analysis  - Run RFM analysis"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run in Docker container"

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	black .
	ruff check --fix .

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-etl:
	python clean_data.py

run-analysis:
	python analysis.py

docker-build:
	docker build -t ecommerce-analytics .

docker-run:
	docker run -v $(PWD)/output:/app/output ecommerce-analytics
