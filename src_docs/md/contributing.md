# Contributing

PlaywrightAuthor welcomes contributions. This guide covers setup, development workflow, coding standards, testing, and pull requests.

## Development Setup

### Prerequisites

- **Python 3.8+** (3.11+ recommended)
- **Git** for version control
- **uv** for dependency management
- **Chrome or Chromium** for testing

### Initial Setup

1. **Fork and Clone**:
```bash
# Fork the repository on GitHub first
git clone https://github.com/yourusername/playwrightauthor.git
cd playwrightauthor
```

2. **Set up Development Environment**:
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv --python 3.11
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

3. **Verify Installation**:
```bash
# Run tests to ensure everything works
python -m pytest

# Check code quality
python -m ruff check
python -m mypy src/

# Run a simple test
python -c "from playwrightauthor import Browser; print('Installation successful!')"
```

### Development Workflow

1. **Create Feature Branch**:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

2. **Make Changes**: Follow coding standards below

3. **Run Quality Checks**:
```bash
# Format and lint code
fd -e py -x uvx autoflake -i {}
fd -e py -x uvx pyupgrade --py312-plus {}
fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}
fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}

# Type checking
python -m mypy src/

# Run tests
python -m pytest -v
```

4. **Commit Changes**:
```bash
git add .
git commit -m "feat: add new feature description"
# Use conventional commit format (see below)
```

5. **Push and Create PR**:
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Coding Standards

### Code Style

**Python Standards**:
- **PEP 8**: Formatting and naming conventions
- **PEP 20**: Keep code simple and explicit
- **PEP 257**: Clear, imperative docstrings
- **Type hints**: Use modern type hints (list, dict, | for unions)

**File Structure**:
- Every file must include a `this_file:` comment with relative path
- Use consistent imports and module organization
- Follow existing patterns in the codebase

### Example Code Style

```python
#!/usr/bin/env python3
# this_file: src/playwrightauthor/example.py

"""
Example module demonstrating coding standards.
"""

from pathlib import Path
from typing import Optional
from loguru import logger


class ExampleClass:
    """Example class with proper documentation and type hints."""
    
    def __init__(self, name: str, timeout: int = 30) -> None:
        """
        Initialize example class.
        
        Args:
            name: The name identifier
            timeout: Timeout in seconds (default: 30)
        """
        self.name = name
        self.timeout = timeout
        logger.debug(f"Created {self.__class__.__name__} with name={name}")
    
    def process_data(self, data: list[dict]) -> dict[str, any]:
        """
        Process input data and return results.
        
        Args:
            data: List of data dictionaries to process
            
        Returns:
            Dictionary containing processing results
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        results = {"processed": len(data), "errors": []}
        
        for item in data:
            try:
                self._process_item(item)
            except Exception as e:
                logger.warning(f"Failed to process item: {e}")
                results["errors"].append(str(e))
        
        return results
    
    def _process_item(self, item: dict) -> None:
        """Private method to process individual item."""
        pass
```

### Documentation Standards

**Docstring Format**:
```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Brief one-line description of what the function does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 10)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When parameter validation fails
        ConnectionError: When unable to connect to browser
    
    Example:
        >>> result = function_name("test", 20)
        >>> assert result is True
    """
```

**Code Comments**:
```python
# Use comments to explain WHY, not WHAT
# Good: Retry connection to handle temporary network issues
# Bad: Increment retry_count variable

def connect_with_retry(self, max_retries: int = 3) -> bool:
    """Connect to browser with retry logic."""
    for attempt in range(max_retries):
        try:
            return self._connect()
        except ConnectionError:
            # Exponential backoff to avoid overwhelming the server
            time.sleep(2 ** attempt)
    
    return False
```

## Testing

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── unit/
│   ├── test_browser.py
│   ├── test_config.py
│   └── test_finder.py
├── integration/
│   ├── test_browser_manager.py
│   └── test_auth.py
├── e2e/
│   └── test_full_workflow.py
└── conftest.py
```

### Writing Tests

**Unit Test Example**:
```python
# tests/unit/test_config.py
# this_file: tests/unit/test_config.py

import pytest
from playwrightauthor import BrowserConfig
from playwrightauthor.exceptions import ConfigurationError


class TestBrowserConfig:
    """Test cases for BrowserConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = BrowserConfig()
        
        assert config.headless is True
        assert config.timeout == 30000
        assert config.debug_port == 9222
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = BrowserConfig(
            headless=False,
            timeout=60000,
            debug_port=9223
        )
        
        assert config.headless is False
        assert config.timeout == 60000
        assert config.debug_port == 9223
    
    def test_invalid_timeout(self):
        """Test validation of invalid timeout."""
        with pytest.raises(ConfigurationError):
            BrowserConfig(timeout=-1000)
    
    def test_config_serialization(self):
        """Test configuration to/from dict conversion."""
        original = BrowserConfig(headless=False, timeout=45000)
        config_dict = original.to_dict()
        restored = BrowserConfig.from_dict(config_dict)
        
        assert restored.headless == original.headless
        assert restored.timeout == original.timeout
    
    @pytest.mark.parametrize("port,expected", [
        (9222, True),
        (80, False),
        (65536, False),
    ])
    def test_port_validation(self, port: int, expected: bool):
        """Test port validation with various values."""
        if expected:
            config = BrowserConfig(debug_port=port)
            assert config.debug_port == port
        else:
            with pytest.raises(ConfigurationError):
                BrowserConfig(debug_port=port)
```

**Integration Test Example**:
```python
# tests/integration/test_browser_manager.py
# this_file: tests/integration/test_browser_manager.py

import pytest
from playwrightauthor import Browser, BrowserConfig
from playwrightauthor.browser_manager import BrowserManager


class TestBrowserManager:
    """Integration tests for browser management."""
    
    def test_browser_lifecycle(self):
        """Test complete browser lifecycle."""
        config = BrowserConfig(headless=True)
        manager = BrowserManager(config)
        
        # Test browser startup
        chrome_path = manager.ensure_browser_available()
        assert chrome_path is not None
        
        # Test browser launch
        process = manager.launch_browser()
        assert process is not None
        assert process.poll() is None  # Process is running
        
        # Test connection
        browser = manager.connect_to_browser()
        assert browser is not None
        
        # Test browser usage
        page = browser.new_page()
        page.goto("data:text/html,<h1>Test</h1>")
        assert "Test" in page.content()
        
        # Test cleanup
        manager.cleanup()
    
    @pytest.mark.slow
    def test_chrome_download(self):
        """Test Chrome for Testing download (slow test)."""
        from playwrightauthor.browser.installer import ChromeInstaller
        
        installer = ChromeInstaller()
        chrome_path = installer.install_latest()
        
        assert chrome_path is not None
        assert Path(chrome_path).exists()
        assert Path(chrome_path).is_file()
```

### Test Fixtures

```python
# tests/conftest.py
# this_file: tests/conftest.py

import pytest
import tempfile
from pathlib import Path
from playwrightauthor import Browser, BrowserConfig


@pytest.fixture
def temp_profile():
    """Create temporary profile directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config(temp_profile):
    """Create test configuration."""
    return BrowserConfig(
        headless=True,
        timeout=10000,
        user_data_dir=str(temp_profile)
    )


@pytest.fixture
def browser_instance(test_config):
    """Create browser instance for testing."""
    with Browser(config=test_config) as browser:
        yield browser


@pytest.fixture(scope="session")
def chrome_executable():
    """Ensure Chrome is available for tests."""
    from playwrightauthor.browser.finder import find_chrome
    
    try:
        return find_chrome()
    except Exception:
        from playwrightauthor.browser.installer import ChromeInstaller
        installer = ChromeInstaller()
        return installer.install_latest()
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/                    # Unit tests only
python -m pytest tests/integration/             # Integration tests only
python -m pytest -m "not slow"                  # Skip slow tests

# Run with coverage
python -m pytest --cov=src/playwrightauthor --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_config.py -v

# Run specific test function
python -m pytest tests/unit/test_config.py::TestBrowserConfig::test_default_config -v
```

### Test Markers

```python
# Slow tests (network operations, downloads)
@pytest.mark.slow
def test_chrome_download():
    pass

# Tests requiring network access
@pytest.mark.network
def test_api_call():
    pass

# Tests requiring GUI (not in CI)
@pytest.mark.gui
def test_visual_features():
    pass

# Platform-specific tests
@pytest.mark.windows
@pytest.mark.macos
@pytest.mark.linux
def test_platform_feature():
    pass
```

## Documentation

### Documentation Structure

Documentation is built with MkDocs Material:

```
src_docs/
├── mkdocs.yml
└── md/
    ├── index.md
    ├── getting-started.md
    ├── basic-usage.md
    └── ...
```

### Building Documentation

```bash
# Install documentation dependencies
uv add --dev mkdocs mkdocs-material mkdocstrings[python]

# Serve documentation locally
cd src_docs
mkdocs serve

# Build documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Documentation Guidelines

**Writing Style**:
- Use clear, concise language
- Include practical examples
- Provide both simple and advanced usage patterns
- Cross-reference related topics

**Code Examples**:
```python
# ✅ Good: Complete, runnable example
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    title = page.title()
    print(f"Page title: {title}")

# ❌ Bad: Incomplete or unclear example
browser = Browser()
page.goto("example.com")
```

**Section Structure**:
```markdown
# Main Topic

Brief introduction explaining what this covers.

## Subsection

### Code Example
\```python
# Example code here
\```

### Explanation

Detailed explanation of the example.

### Common Issues

- Issue 1: Solution description
- Issue 2: Solution description

## Next Steps

- Link to [Related Topic](related.md)
- Check [Advanced Guide](advanced.md) for more
```

## Pull Request Process

### Before Submitting

**Checklist**:
- [ ] Code follows style guidelines
- [ ] Tests pass (`python -m pytest`)
- [ ] Type checking passes (`python -m mypy src/`)
- [ ] Linting passes (`python -m ruff check`)
- [ ] Documentation updated if needed
- [ ] `CHANGELOG.md` updated
- [ ] Commit messages follow conventional format

### Conventional Commits

Use conventional commit format:

```bash
# Feature additions
git commit -m "feat: add support for custom user agents"
git commit -m "feat(auth): implement GitHub OAuth integration"

# Bug fixes
git commit -m "fix: resolve Chrome download timeout on slow networks"
git commit -m "fix(browser): handle process cleanup on Windows"

# Documentation updates
git commit -m "docs: add troubleshooting guide for Docker"
git commit -m "docs(api): improve BrowserConfig examples"

# Refactoring
git commit -m "refactor: simplify browser connection logic"

# Performance improvements
git commit -m "perf: optimize Chrome process detection"

# Breaking changes
git commit -m "feat!: change default timeout from 30s to 60s"
```

### PR Template

When creating a pull request, include:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] New tests added for new functionality
- [ ] All existing tests pass
- [ ] Manual testing performed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] Changes tested locally
```

### Code Review Process

**For Contributors**:
1. Address all feedback promptly
2. Keep discussions focused on the code
3. Be open to suggestions and improvements
4. Update PR based on review comments

**For Reviewers**:
1. Focus on code quality, not personal preferences
2. Provide constructive feedback with examples
3. Acknowledge good practices and improvements
4. Test changes locally when possible

## Release Process

### Version Management

PlaywrightAuthor uses semantic versioning (SemVer):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

### Release Workflow

**For Maintainers**:

1. **Update Version**:
```bash
# Update version in pyproject.toml
# Update CHANGELOG.md with release notes
```

2. **Create Release**:
```bash
git tag v1.2.3
git push origin v1.2.3
```

3. **GitHub Actions** automatically:
   - Runs full test suite
   - Builds distributions
   - Publishes to PyPI
   - Creates GitHub release

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different perspectives and experiences

### Getting Help

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Check existing docs first
- **Code**: Look at examples in the repository

### Reporting Issues

**Bug Reports**:
```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Expected vs actual behavior

## Environment
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.0]
- PlaywrightAuthor: [e.g., 1.0.0]
- Chrome: [e.g., 119.0.6045.105]

## Additional Context
Any other relevant information.
```

**Feature Requests**:
```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How do you envision this working?

## Alternatives Considered
What other solutions have you considered?
```

## Development Tips

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use verbose browser for visual debugging
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    headless=False,
    chrome_args=["--auto-open-devtools-for-tabs"]
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    page.pause()  # Opens Playwright Inspector
```

### Performance Testing

```python
# Simple performance benchmarking
import time
from playwrightauthor import Browser

def benchmark_operation():
    start = time.time()
    
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://example.com")
        # Operation to benchmark
    
    end = time.time()
    print(f"Operation took: {end - start:.2f} seconds")

benchmark_operation()
```

### Local Development

```bash
# Install in development mode
pip install -e .

# Run specific components
python -m playwrightauthor.cli status
python -m playwrightauthor.browser.finder

# Test with different Python versions
pyenv install 3.8.18 3.9.18 3.10.13 3.11.7
tox  # If tox.ini is configured
```

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security@terragonlabs.com
2. Include detailed description
3. Provide reproduction steps if possible
4. Allow time for investigation before disclosure

### Security Best Practices

- Never commit secrets or credentials
- Use secure defaults in configuration
- Validate all user inputs
- Handle sensitive data carefully
- Follow principle of least privilege

## Thank You

Your contributions help make browser automation more accessible and reliable.

## Next Steps

- Review the [API Reference](api-reference.md) for implementation details
- Check [Troubleshooting](troubleshooting.md) for common development issues
- Join GitHub Discussions to connect with other contributors