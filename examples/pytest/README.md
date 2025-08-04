# PlaywrightAuthor + pytest Integration

This example demonstrates how to integrate PlaywrightAuthor with pytest for robust browser automation testing.

## Features Demonstrated

- **Pytest Fixtures**: Reusable browser setup with proper teardown
- **Profile Management**: Testing with different user profiles
- **Error Handling**: Robust error handling and recovery
- **Parallel Testing**: Running tests concurrently with different profiles
- **Authentication Testing**: Testing login flows and authenticated scenarios
- **Performance Testing**: Basic performance assertions

## Installation

```bash
pip install playwrightauthor pytest pytest-asyncio pytest-xdist
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests in parallel (requires pytest-xdist)
pytest -n 4

# Run specific test categories
pytest -m "smoke"
pytest -m "auth"
pytest -m "performance"
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_basic.py` - Basic browser automation tests
- `test_authentication.py` - Login and authentication testing
- `test_profiles.py` - Multi-profile testing scenarios
- `test_performance.py` - Performance and reliability tests
- `test_async.py` - Async browser testing patterns

## Best Practices

1. **Use Fixtures**: Always use pytest fixtures for browser setup
2. **Profile Isolation**: Use different profiles for different test categories
3. **Error Recovery**: Implement proper error handling and cleanup
4. **Timeouts**: Set appropriate timeouts for network operations
5. **Parallel Safe**: Ensure tests can run in parallel without conflicts