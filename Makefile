# Makefile for Proofpoint ITM API Client

.PHONY: help install test test-fast test-cov test-integration clean build build-check publish publish-test

help:
	@echo "Proofpoint ITM API Client - Available Commands"
	@echo "=============================================="
	@echo "Development:"
	@echo "  make install          - Install package and test dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all unit tests"
	@echo "  make test-fast        - Run tests without slow integration tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make test-integration - Run integration tests (requires .env)"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  make build            - Build package for distribution"
	@echo "  make build-check      - Check built package"
	@echo "  make publish-test     - Publish to Test PyPI"
	@echo "  make publish          - Publish to production PyPI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove test artifacts and cache"
	@echo "  make clean-build      - Remove build artifacts"
	@echo ""
	@echo "Using UV package manager:"
	@echo "  All commands use 'uv' automatically"

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

clean-build:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

build: clean-build
	@echo "Building package..."
	uv build
	@echo ""
	@echo "Build complete! Files created in dist/"
	@ls -lh dist/

build-check: build
	@echo "Checking built package..."
	uv pip install twine
	uv run twine check dist/*

publish-test: build-check
	@echo "Publishing to Test PyPI..."
	@echo "Make sure you have TWINE_USERNAME and TWINE_PASSWORD set"
	uv run twine upload --repository testpypi dist/*
	@echo ""
	@echo "Test installation with:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ proofpoint-itm"

publish: build-check
	@echo "Publishing to PyPI..."
	@echo "Make sure you have TWINE_USERNAME and TWINE_PASSWORD set"
	@read -p "Are you sure you want to publish to PyPI? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		uv run twine upload dist/*; \
		echo ""; \
		echo "Published! Install with:"; \
		echo "  pip install proofpoint-itm"; \
	else \
		echo "Publish cancelled."; \
	fi
