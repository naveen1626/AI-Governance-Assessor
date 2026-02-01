# Contributing to AI Dual-Use Risk Assessor

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI_Governance.git
   cd AI_Governance
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/AI_Governance.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/OWNER/AI_Governance/issues)
- If not, create a new issue with:
  - Clear, descriptive title
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)
  - Relevant logs or screenshots

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would benefit the project

### Contributing Code

Areas where contributions are especially welcome:

1. **New LLM Providers**: Add support for additional LLM APIs
2. **Framework Enhancements**: Improve the 12-axis scoring framework
3. **Regulatory Updates**: Update regulatory framework mappings
4. **UI/UX Improvements**: Enhance the web interface
5. **Testing**: Add unit tests and integration tests
6. **Documentation**: Improve docs, tutorials, examples
7. **Internationalization**: Add multi-language support

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- A code editor (VS Code recommended)

### Setup Steps

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Copy environment file
cp .env.example .env
# Add your API key to .env

# Run the application
python run.py
```

### Project Structure

```
app/
├── main.py           # Application entry point
├── config.py         # Configuration management
├── models.py         # Pydantic models
├── routes/           # API endpoints
├── services/         # Business logic
└── templates/        # HTML templates

tests/                # Test files
data/                 # Data files (axes config, assessments)
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Format code**:
   ```bash
   black app/ tests/
   flake8 app/ tests/
   ```

4. **Update documentation** if needed

### Submitting a PR

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

4. Wait for review and address feedback

### PR Review Criteria

- Code follows project style guidelines
- Tests pass and new tests added if applicable
- Documentation updated
- No merge conflicts
- Meaningful commit messages

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 100 characters
- Use type hints where practical

### Naming Conventions

```python
# Variables and functions: snake_case
risk_score = calculate_risk_score(paper_data)

# Classes: PascalCase
class RiskAssessment:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings:

```python
def score_research(title: str, abstract: str) -> tuple[RiskScores, list[RiskAxis], str]:
    """Score a research paper using the 12-axis framework.

    Args:
        title: The paper title.
        abstract: The paper abstract.

    Returns:
        A tuple containing:
            - RiskScores object with all axis scores
            - List of RiskAxis definitions used
            - Detected category string or None
    """
```

### Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Use imperative mood: "Fix bug" not "Fixes bug"
- Keep first line under 72 characters
- Reference issues when applicable: "Fix scoring bug (#42)"

Example:
```
Add support for Gemini API provider

- Implement call_google() function in risk_scorer.py
- Add GOOGLE_API_KEY to config.py
- Update .env.example with new configuration
- Add tests for Google provider

Closes #15
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_multi_category_assessments.py

# Run with verbose output
pytest -v tests/
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures for setup

Example:
```python
import pytest
from app.services.governance import compute_tier
from app.models import RiskScores, Tier

@pytest.fixture
def sample_scores():
    return RiskScores(scores={
        "A1": AxisScore(score=2, rationale="Test"),
        # ... other axes
    })

def test_compute_tier_medium(sample_scores):
    tier = compute_tier(sample_scores, Dissemination.PREPRINT, Audience.RESEARCHERS)
    assert tier == Tier.MEDIUM
```

## Questions?

- Open a [Discussion](https://github.com/OWNER/AI_Governance/discussions) for general questions
- Join our community chat (if available)
- Contact maintainers directly for sensitive matters

Thank you for contributing!
