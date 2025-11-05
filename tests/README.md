# Proofpoint ITM API Client Tests

This directory contains the test suite for the Proofpoint ITM API client library.

## Quick Start

```bash
# 1. Install package and test dependencies
make install
# or: uv pip install -e ".[test]"

# 2. Run all tests
make test
# or: uv run pytest tests/ -v

# 3. Run with coverage
make test-cov
# or: uv run pytest tests/ --cov=proofpoint_itm --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── test_client_init.py         # Authentication & initialization tests
├── test_client_rules.py        # Rules CRUD operations tests
├── test_client_predicates.py   # Predicates CRUD operations tests
├── test_client_tags.py         # Tags CRUD operations tests
├── test_client_search.py       # Search methods tests
├── test_client_endpoints.py    # Endpoints methods tests
├── test_client_workflow.py     # Workflow status update tests
├── test_client_errors.py       # Error handling tests
└── integration/                # Integration tests
    ├── __init__.py
    └── test_integration.py     # Real API integration tests
```

## Running Tests

### Install Package and Test Dependencies

**Using UV (recommended):**
```bash
# Install package in editable mode + test dependencies
uv pip install -e ".[test]"
```

**Using pip:**
```bash
# Install package in editable mode + test dependencies
pip install -e ".[test]"
```

### Run All Unit Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_client_rules.py -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=proofpoint_itm --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only slow/integration tests
pytest tests/ -m slow -v
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

## Integration Tests

Integration tests can run in two modes:

### 1. Development Mode (Default - Safe)

Development mode doesn't make real API calls. It returns request details instead.

```bash
pytest tests/integration/ -v
```

### 2. Real API Mode (Requires Credentials)

To test against the real API:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your credentials in `.env`:
   ```
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   TENANT_ID=your-tenant-id
   INTEGRATION_TEST=true
   ```

3. Run integration tests:
   ```bash
   INTEGRATION_TEST=true pytest tests/integration/ -v
   ```

**Warning:** Real API tests will make actual API calls and may create/modify resources.

## Writing New Tests

### Unit Test Example

```python
import pytest
import responses

def test_get_rules_success(mock_client, sample_rule_data):
    """Test successful retrieval of rules."""
    url = f"{mock_client.base_url}/ruler/rules"
    
    responses.add(
        responses.GET,
        url,
        json={"data": [sample_rule_data]},
        status=200
    )
    
    result = mock_client.get_rules()
    
    assert isinstance(result, list)
    assert len(result) == 1
```

### Integration Test Example

```python
@pytest.mark.slow
def test_get_rules_real_api(integration_client):
    """Test get_rules against real API."""
    result = integration_client.get_rules()
    
    assert isinstance(result, list)
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_config` - Mock configuration dictionary
- `mock_client` - Mock ITM client with patched auth
- `development_client` - Client in development mode
- `mock_responses` - Activated responses library
- `sample_rule_data` - Sample rule data
- `sample_predicate_data` - Sample predicate data
- `sample_tag_data` - Sample tag data
- And more...

## Makefile Commands

Convenient shortcuts for common tasks:

```bash
make help             # Show all available commands

# Development
make install          # Install package and test dependencies

# Testing
make test             # Run all unit tests
make test-fast        # Run tests without slow integration tests
make test-cov         # Run tests with coverage report
make test-integration # Run integration tests (requires .env)

# Building & Publishing
make build            # Build package for distribution
make build-check      # Check built package
make publish-test     # Publish to Test PyPI
make publish          # Publish to production PyPI

# Cleanup
make clean            # Remove test artifacts and cache
make clean-build      # Remove build artifacts
```

## Test Coverage

### What's Tested

**Client Methods:**
- ✅ Authentication & initialization
- ✅ Rules CRUD operations
- ✅ Predicates CRUD operations
- ✅ Tags CRUD operations (including `add_activity_tag`)
- ✅ Search methods (depot, notification, ruler, activity, registry)
- ✅ Endpoints methods (with custom queries)
- ✅ Workflow updates (`update_event_workflow`)
- ✅ Activity methods (assignee, tags)
- ✅ Error handling (HTTP errors, network errors, malformed responses)

**Integration Tests:**
- ✅ Activity search for alerts
- ✅ Add tags to real alerts
- ✅ Add assignees to real alerts
- ✅ Update workflow status on real alerts
- ✅ Get endpoints with custom queries
- ✅ Tags, policies, and other resources

**Test Count:** 100+ tests across unit and integration suites

### Bugs Found & Fixed

The test suite discovered and helped fix several real bugs:
1. **`activity_search` URL bug** - Duplicate `/v2/apis/` in endpoint
2. **`get_conditions` response parsing** - Missing `.json()` call
3. **JSONL streaming** - Improper handling of `stream=True` responses
4. **`update_event_workflow` body structure** - Incorrect nested structure

### Coverage Goals

- **Target:** 90%+ code coverage
- **Priority:** All public methods should have tests
- **Focus:** Response parsing, error handling, parameter merging, JSONL streaming

## Continuous Integration

Tests should be run:
- On every pull request
- On every commit to main branch
- Nightly (including integration tests)

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed in development mode:

```bash
pip install -e .
```

### Authentication Errors in Integration Tests

Check that your `.env` file has valid credentials and is in the project root.

**Required environment variables:**
```bash
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
TENANT_ID=your-tenant-id
INTEGRATION_TEST=true

# Optional for specific tests
TEST_ADMIN_ID=your-admin-user-id  # For assignee tests
```

### Timeout Errors

Increase the timeout in the client initialization:

```python
client = ITMClient(config, timeout=60)
```

## Additional Resources

- [Testing Strategy Document](../TESTING_STRATEGY.md)
- [pytest Documentation](https://docs.pytest.org/)
- [responses Library](https://github.com/getsentry/responses)
