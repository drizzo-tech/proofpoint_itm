# Testing Strategy for Proofpoint ITM API Client

## Overview

This document outlines the testing strategy for the Proofpoint ITM API client library. The goal is to ensure all client methods return proper responses and handle errors correctly.

## Testing Approach

### 1. Unit Tests with Mocking (Primary)
- Mock HTTP requests using `responses` or `unittest.mock`
- Test response parsing logic without hitting real API
- Fast execution, no API credentials needed
- Ideal for CI/CD pipelines

### 2. Integration Tests (Optional)
- Use `development_mode=True` flag for safe testing
- Or use test credentials against a sandbox environment
- Validates actual API behavior
- Slower, requires credentials

## Test Categories

### A. Authentication & Initialization
- ✅ Token retrieval success
- ✅ Token retrieval failure (invalid credentials)
- ✅ Session setup with proper headers
- ✅ Base URL construction

### B. GET Methods (Read Operations)
Test all methods that retrieve data:
- `get_rules()`, `get_rule(id)`
- `get_predicates()`, `get_predicate(id)`
- `get_tags()`, `get_tag(id)`
- `get_agent_policies()`, `get_agent_policy(id)`
- `get_dictionaries()`, `get_dictionary(id)`
- `get_detectors()`, `get_detector(id)`
- `get_detector_sets()`, `get_detector_set(id)`
- `get_smartids()`
- `get_endpoints()`

**Test scenarios:**
- ✅ Successful response with data
- ✅ Response with `data` array vs direct object
- ✅ Empty results
- ✅ HTTP errors (404, 500, etc.)
- ✅ Timeout handling
- ✅ Parameter merging (includes, custom params)

### C. POST Methods (Create Operations)
Test creation methods:
- `create_rule()`, `create_predicate()`, `create_tag()`
- `create_agent_policy()`, `create_notification_policy()`
- `create_dictionary()`, `create_detector()`, `create_detector_set()`

**Test scenarios:**
- ✅ Successful creation with returned ID
- ✅ Test mode flag (returns fake UUID)
- ✅ Development mode (returns request details)
- ✅ Validation errors
- ✅ Duplicate resource errors

### D. PUT/PATCH Methods (Update Operations)
Test update methods:
- `update_rule()`, `update_predicate()`, `update_tag()`
- `update_agent_policy()`, `update_notification_policy()`
- `update_dictionary()`, `update_detector()`, `update_detector_set()`
- `overwrite_predicate()`, `overwrite_agent_policy()`

**Test scenarios:**
- ✅ Successful update
- ✅ PATCH vs PUT behavior
- ✅ Resource not found (404)
- ✅ Validation errors

### E. DELETE Methods
Test deletion methods:
- `delete_rule()`, `delete_predicate()`, `delete_dictionary()`
- `delete_detector_set()`

**Test scenarios:**
- ✅ Successful deletion
- ✅ Resource not found (404)
- ✅ Cascade deletion behavior

### F. Search Methods
Test search endpoints:
- `depot_search()`, `notification_search()`, `ruler_search()`
- `activity_search()`, `registry_search()`

**Test scenarios:**
- ✅ Query construction
- ✅ Streaming vs regular responses
- ✅ Pagination (offset, limit)
- ✅ Empty results
- ✅ Complex queries

### G. Special Methods
- `add_activity_tag()`, `add_activity_assignee()`
- `update_event_workflow()`
- `publish_config()`
- `get_conditions()` (filtered predicates)

### H. Error Handling
- ✅ Network errors
- ✅ Timeout errors
- ✅ HTTP status errors (4xx, 5xx)
- ✅ Malformed JSON responses
- ✅ Token expiration and refresh

### I. Edge Cases
- ✅ None/empty parameters
- ✅ Invalid IDs
- ✅ Special characters in data
- ✅ Large payloads
- ✅ Concurrent requests

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_client_init.py         # Authentication & initialization
├── test_client_rules.py        # Rules CRUD operations
├── test_client_predicates.py  # Predicates CRUD operations
├── test_client_tags.py         # Tags CRUD operations
├── test_client_policies.py     # Agent policies CRUD operations
├── test_client_dictionaries.py # Dictionaries CRUD operations
├── test_client_detectors.py    # Detectors CRUD operations
├── test_client_search.py       # Search methods
├── test_client_special.py      # Special methods
├── test_client_errors.py       # Error handling
└── integration/                # Optional integration tests
    ├── __init__.py
    └── test_integration.py
```

## Tools & Dependencies

- **pytest** - Test framework
- **pytest-mock** - Mocking utilities
- **responses** - HTTP request mocking
- **pytest-cov** - Code coverage
- **python-dotenv** - Environment variable management (for integration tests)

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock responses pytest-cov python-dotenv

# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=proofpoint_itm --cov-report=html

# Run specific test file
pytest tests/test_client_rules.py -v

# Run integration tests (requires credentials)
pytest tests/integration/ -v
```

## Coverage Goals

- **Target:** 90%+ code coverage
- **Priority:** All public methods should have tests
- **Focus areas:** Response parsing, error handling, parameter merging

## Continuous Integration

Tests should run on:
- Every pull request
- Every commit to main branch
- Nightly builds (including integration tests)

## Known Issues to Test

Based on recent fixes, ensure tests cover:
1. Methods returning `resp.json()` vs `resp.json()["data"]`
2. Proper handling of `includes` parameter
3. Correct endpoint URL construction
4. Response structure consistency
5. Error message clarity
