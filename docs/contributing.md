# Contributing to QFZZ

Thank you for your interest in contributing to QFZZ! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and constructive. We're building this together.

## Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/QFZZ.git
cd QFZZ
```

### 2. Set Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=qfzz tests/

# Run specific test
pytest tests/test_core.py::test_station_initialization
```

### Code Style

We use Black for formatting and Flake8 for linting:

```bash
# Format code
black qfzz/ tests/ examples/

# Check linting
flake8 qfzz/ tests/ examples/

# Type checking
mypy qfzz/
```

### Documentation

Build and preview documentation:

```bash
# Build
mkdocs build

# Serve locally
mkdocs serve

# Visit http://localhost:8000
```

## Contribution Areas

### 1. Core Features

**High Priority:**
- Real LLM integration (Llama, Mistral, Gemma)
- Actual music streaming implementation
- Real blockchain network integration (Ethereum, Polygon)

**Medium Priority:**
- Advanced recommendation algorithms
- Social features and community connections
- Mobile app support

### 2. Datasets

**We Need:**
- Dataset loaders for popular opensource music datasets
- Quality scoring algorithms
- Metadata extraction tools
- License validation utilities

### 3. Edge Optimization

**Areas:**
- Model quantization implementations
- Pruning algorithms
- More efficient caching strategies
- Device-specific optimizations

### 4. Documentation

**Help With:**
- Tutorial videos
- More usage examples
- Translation to other languages
- API documentation improvements

### 5. Testing

**Needed:**
- Unit tests for all modules
- Integration tests
- Performance benchmarks
- Edge device testing

## Pull Request Process

### 1. Make Your Changes

```bash
# Make changes
# Add tests
# Update documentation
```

### 2. Test Everything

```bash
# Run tests
pytest tests/

# Check code style
black --check qfzz/
flake8 qfzz/

# Build docs
mkdocs build
```

### 3. Commit

Use clear commit messages:

```bash
git add .
git commit -m "Add feature: description of feature"
```

Good commit messages:
- `Add LLM integration for Llama 3`
- `Fix bug in trust score calculation`
- `Update documentation for edge deployment`
- `Add tests for blockchain verification`

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

### 5. PR Requirements

Your PR should:
- [ ] Pass all tests
- [ ] Follow code style guidelines
- [ ] Include documentation updates
- [ ] Have clear commit messages
- [ ] Include tests for new features
- [ ] Not break existing functionality

## Code Guidelines

### Python Style

```python
# Good
def calculate_trust_score(user_id: str, interactions: int) -> float:
    """Calculate user trust score.

    Args:
        user_id: User identifier
        interactions: Number of interactions

    Returns:
        Trust score between 0.0 and 1.0
    """
    base_score = 0.5
    bonus = interactions * 0.01
    return min(1.0, base_score + bonus)


# Not so good
def calc_trust(uid, i):
    return 0.5 + i * 0.01
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When this happens

    Examples:
        >>> function_name("test", 42)
        True
    """
```

### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional

def process_items(items: List[str], config: Optional[Dict[str, Any]] = None) -> int:
    """Process items."""
    if config is None:
        config = {}
    return len(items)
```

### Error Handling

```python
# Good
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return default_value

# Not so good
try:
    result = risky_operation()
except:
    pass
```

## Testing Guidelines

### Unit Tests

```python
import pytest
from qfzz import PersonalizedDJ

def test_dj_greeting_new_user():
    """Test DJ greeting for new user"""
    dj = PersonalizedDJ()
    greeting = dj.greet_user("user_001", "Alice")

    assert "Alice" in greeting
    assert "Welcome" in greeting
    assert "user_001" in dj.user_profiles


def test_dj_trust_score_increases():
    """Test trust score increases with interactions"""
    dj = PersonalizedDJ()
    initial_score = dj.get_trust_score("user_001")

    dj.interact("user_001", "Hello")

    new_score = dj.get_trust_score("user_001")
    assert new_score > initial_score
```

### Integration Tests

```python
def test_full_station_workflow():
    """Test complete station workflow"""
    # Initialize station
    station = QFZZStation()
    station.initialize()
    station.start()

    # Verify running
    assert station.is_running

    # Stop
    station.stop()
    assert not station.is_running
```

## Documentation Guidelines

### Markdown Style

```markdown
# Main Heading

Short introduction paragraph.

## Section Heading

Content here.

### Subsection

More specific content.

#### Code Example

```python
# Code goes here
```

### Links

[Link text](url)
```

### API Documentation

Document all public APIs:

```python
class MyClass:
    """Short class description.

    Longer description with details about the class,
    its purpose, and how to use it.

    Attributes:
        attribute1: Description of attribute1
        attribute2: Description of attribute2

    Examples:
        >>> obj = MyClass()
        >>> obj.do_something()
    """

    def public_method(self, param: str) -> int:
        """Document public methods.

        Args:
            param: Parameter description

        Returns:
            Return value description
        """
        return 42

    def _private_method(self):
        """Private methods should also be documented."""
        pass
```

## Feature Requests

Have an idea? Open an issue:

1. Go to [GitHub Issues](https://github.com/fuzzywigg/QFZZ/issues)
2. Click "New Issue"
3. Describe your feature
4. Explain why it's useful
5. Provide examples if possible

## Bug Reports

Found a bug? Report it:

1. Check if already reported
2. Create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Your environment (OS, Python version)
   - Error messages

Example:
```markdown
## Bug: Trust score exceeds 1.0

### Steps to Reproduce
1. Create DJ
2. Add 200 interactions
3. Check trust score

### Expected
Trust score should be 1.0 (clamped)

### Actual
Trust score is 2.5

### Environment
- OS: Ubuntu 22.04
- Python: 3.9.5
- QFZZ: 0.1.0
```

## Areas We Need Help

### Critical
- [ ] LLM integration
- [ ] Music streaming implementation
- [ ] Blockchain network integration

### Important
- [ ] Test coverage improvement
- [ ] Performance optimization
- [ ] Mobile app development

### Nice to Have
- [ ] UI/UX improvements
- [ ] More examples
- [ ] Tutorial videos
- [ ] Translations

## Community

- **GitHub**: [fuzzywigg/QFZZ](https://github.com/fuzzywigg/QFZZ)
- **Issues**: [Report bugs](https://github.com/fuzzywigg/QFZZ/issues)
- **Discussions**: [Ask questions](https://github.com/fuzzywigg/QFZZ/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Reach out to maintainers

Thank you for contributing to QFZZ! 🎵✨
