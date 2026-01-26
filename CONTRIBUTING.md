# Contributing to QFZZ FuzzyRadio

Thank you for your interest in contributing to QFZZ! This guide will help you understand our development process and get your contributions merged quickly.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [The Stage vs Backstage Pattern](#the-stage-vs-backstage-pattern)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Templates](#issue-templates)

## Code of Conduct

Be respectful, constructive, and professional. We're building something cool together.

## The Stage vs Backstage Pattern

QFZZ operates in two distinct modes, and understanding this is crucial:

### Stage (User-Facing)

**What it is**: The DJ's personality, on-air content, user interactions.

**Rules**:
- Never break the 4th wall
- No mentions of AI, LLMs, algorithms, or technology
- The DJ is a real person with opinions and personality
- Content should feel like authentic radio

**Examples**:
- ✅ "I've got the perfect track to get your Friday started right!"
- ✅ "You're listening to QFZZ, where the music never stops"
- ❌ "As an AI, I've analyzed your preferences..."
- ❌ "My language model suggests this track..."

**Where it applies**:
- DJ prompts and responses
- Station IDs and transitions
- User-facing messages
- Anything a listener sees/hears

### Backstage (Technical)

**What it is**: Code, documentation, technical implementation, developer communication.

**Rules**:
- Be precise and technical
- Document implementation details
- Explain algorithms and architecture
- Use proper terminology (LLM, API, stigmergy, etc.)

**Examples**:
- Code comments explaining logic
- Technical documentation
- API documentation
- This file (CONTRIBUTING.md)
- Issue discussions

**Where it applies**:
- Python code and comments
- README.md and technical docs
- GitHub issues and PRs
- `.context/` documentation

### Why This Matters

The Stage/Backstage split maintains the illusion for users while allowing developers to work efficiently. When writing code, you're backstage. When writing DJ content, you're on stage.

**Key principle**: Context determines mode. Files in `qfzz/dj/prompts/` are stage. Files in `qfzz/core/` are backstage.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- At least one LLM API key (or Ollama installed locally)

### Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/QFZZ.git
cd QFZZ

# 3. Install dependencies
make install-dev

# 4. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run tests to verify setup
make test

# 6. Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Understanding the Codebase

1. **Read `.context/substrate.md`**: Project overview and architecture
2. **Read `.context/agents.md`**: Quick start guide for contributors
3. **Explore `qfzz/core/`**: Core infrastructure (state, LLM router)
4. **Run tests**: `make test` - see what's being tested
5. **Check issues**: Look at open issues for areas needing work

## Development Workflow

### 1. Pick a Task

- Check [GitHub Issues](https://github.com/fuzzywigg/QFZZ/issues)
- Look at the [Project Board](https://github.com/fuzzywigg/QFZZ/projects)
- Comment on an issue to claim it

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write tests first (TDD approach preferred)
- Implement the feature with minimal changes
- Keep commits small and focused
- Write clear commit messages

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_your_module.py

# Check coverage
pytest --cov=qfzz --cov-report=html
```

### 5. Format and Lint

```bash
# Format code
make format

# Run linter
make lint

# Auto-fix issues
ruff check --fix qfzz/ tests/
```

### 6. Commit

```bash
git add .
git commit -m "Add feature X: brief description"
```

**Commit message format**:
```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

**Types**: feat, fix, docs, test, refactor, style, chore

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- **Line length**: 100 characters max
- **Formatting**: Use `black` and `isort` (run `make format`)
- **Linting**: Must pass `ruff` checks
- **Type hints**: Encouraged but not required
- **Docstrings**: Required for public functions and classes

### Code Organization

```python
"""Module docstring explaining purpose."""

import standard_library
import third_party_library

from qfzz.core import something


class MyClass:
    """Class docstring."""
    
    def public_method(self, arg: str) -> bool:
        """
        Method docstring explaining what it does.
        
        Args:
            arg: Description of argument
            
        Returns:
            Description of return value
        """
        return True
    
    def _private_method(self):
        """Private methods still need docstrings."""
        pass
```

### Security

- **Never commit secrets**: Use `.env` for all sensitive data
- **Use environment variables**: `os.getenv()` for configuration
- **Pre-commit hooks**: Will catch secrets automatically
- **Sanitize inputs**: Especially for user-facing features

### Best Practices

1. **DRY**: Don't Repeat Yourself
2. **KISS**: Keep It Simple, Stupid
3. **YAGNI**: You Aren't Gonna Need It (don't over-engineer)
4. **Test-Driven**: Write tests first
5. **Document**: Explain *why*, not just *what*

## Testing Requirements

### Coverage

- Minimum **80% code coverage** required
- New features must include tests
- Bug fixes must include regression tests

### Test Structure

```python
"""Tests for module X"""

import pytest

from qfzz.module import function_to_test


@pytest.fixture
def my_fixture():
    """Fixture docstring."""
    return setup_test_data()


class TestMyFeature:
    """Test class for feature X."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        result = function_to_test("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case Y."""
        result = function_to_test("")
        assert result is None
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Running Tests

```bash
# All tests
make test

# Specific file
pytest tests/test_state.py

# Specific test
pytest tests/test_state.py::TestStateManager::test_current_track_operations

# With coverage report
pytest --cov=qfzz --cov-report=html
open htmlcov/index.html
```

### Mocking External Services

**Always mock external API calls in tests**. Don't waste money or rate limits.

```python
from unittest.mock import patch, MagicMock

@patch('qfzz.core.llm_router.genai')
def test_google_provider(mock_genai):
    """Test Google provider with mocked API."""
    mock_response = MagicMock()
    mock_response.text = "Mocked response"
    mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
    
    # Test code here
```

## Pull Request Process

### Before Creating PR

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linter passes (`make lint`)
- [ ] Coverage is >80%
- [ ] No secrets committed
- [ ] Documentation updated (if needed)

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage >80%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No secrets committed
```

### Review Process

1. **Automated checks**: CI runs tests and linting
2. **Code review**: Maintainer reviews your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged

### After Merge

- Delete your branch (GitHub will prompt)
- Update your local main: `git checkout main && git pull upstream main`

## Issue Templates

### Bug Report

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.

**Environment**
- OS: [e.g., macOS]
- Python version: [e.g., 3.11]
- QFZZ version: [e.g., 0.1.0]
```

### Feature Request

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Clear description of what you want.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other relevant information.
```

## Questions?

- **Technical questions**: Open a GitHub issue with the `question` label
- **Quick questions**: Check `.context/agents.md` or `.context/substrate.md`
- **Bugs**: Use the bug report template

## License

By contributing to QFZZ, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to QFZZ! Together we're building something special.
