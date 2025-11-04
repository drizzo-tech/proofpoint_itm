# Makefile for Proofpoint ITM API Client

.PHONY: help install test test-fast test-cov test-integration clean

help:
	@echo "Proofpoint ITM API Client - Available Commands"
	@echo "=============================================="
	@echo "make install          - Install package and test dependencies"
	@echo "make test             - Run all unit tests"
	@echo "make test-fast        - Run tests without slow integration tests"
	@echo "make test-cov         - Run tests with coverage report"
	@echo "make test-integration - Run integration tests (requires .env)"
	@echo "make clean            - Remove test artifacts and cache"
	@echo ""
	@echo "Using UV package manager:"
	@echo "  All commands use 'uv run pytest' automatically"

install:
	uv pip install -e ".[test]"

test:
	uv run pytest tests/ -v

test-fast:
	uv run pytest tests/ -v -m "not slow"

test-cov:
	uv run pytest tests/ --cov=proofpoint_itm --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-integration:
	INTEGRATION_TEST=true uv run pytest tests/integration/ -v

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf test-results.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
