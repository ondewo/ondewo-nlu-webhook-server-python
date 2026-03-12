# Development Guide

This guide provides comprehensive instructions for setting up and working with the ONDEWO NLU Webhook Server Python project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Environment Setup](#development-environment-setup)
- [VS Code / Cursor Setup](#vs-code--cursor-setup)
- [Dev Container Setup](#dev-container-setup)
- [Code Quality Tools](#code-quality-tools)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.14** or higher
- **uv** - Fast Python package installer (recommended)
- **Git** - Version control
- **Docker** and **Docker Compose** - For containerized development
- **Make** - Build automation

### Optional but Recommended

- **VS Code** or **Cursor** - IDE with Python support
- **ngrok** - For exposing local server to the internet

### Installing UV

UV is a fast Python package installer and resolver:

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ondewo/ondewo-nlu-webhook-server-python.git
cd ondewo-nlu-webhook-server-python
```

### 2. Setup Local Development Environment

The project includes a Makefile with convenient commands:

```bash
# Full setup (installs dependencies, pre-commit hooks, etc.)
make setup_developer_environment_locally
```

This command will:
- Install system dependencies (apt packages)
- Install Python dependencies with uv
- Install pre-commit hooks
- Copy Docker configuration

### 3. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3.14 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## VS Code / Cursor Setup

The project includes comprehensive VS Code/Cursor configuration:

### Configuration Files

- `.vscode/settings.json` - Editor settings, Python configuration, linting, formatting
- `.vscode/launch.json` - Debug configurations
- `.vscode/tasks.json` - Build and test tasks
- `.vscode/extensions.json` - Recommended extensions
- `.cursorrules` - Cursor AI coding standards

### Recommended Extensions

The following extensions will be recommended when you open the project:

**Essential:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Black Formatter (ms-python.black-formatter)
- MyPy Type Checker (ms-python.mypy-type-checker)

**Recommended:**
- Docker (ms-azuretools.vscode-docker)
- GitLens (eamodio.gitlens)
- Coverage Gutters (ryanluker.vscode-coverage-gutters)
- EditorConfig (editorconfig.editorconfig)

### Test Discovery in VS Code/Cursor

The project is configured for automatic test discovery:

1. **Open Testing Panel**: Click the beaker icon in the sidebar or press `Ctrl+Shift+T` (Cmd+Shift+T on macOS)
2. **Discover Tests**: Tests should automatically appear in the testing panel
3. **Run Tests**: Click the play button next to any test or test file
4. **Debug Tests**: Click the debug icon next to any test

**Test Markers:**
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests

### Debug Configurations

Available debug configurations in VS Code/Cursor:

- **Python: Current File** - Debug the currently open file
- **Python: Pytest - Current File** - Debug tests in current file
- **Python: Pytest - All Tests** - Debug all tests
- **Python: Pytest - Unit Tests** - Debug only unit tests
- **Python: Pytest - Integration Tests** - Debug only integration tests
- **Python: Pytest - E2E Tests** - Debug only end-to-end tests
- **Python: Webhook Server (Local)** - Debug the webhook server locally
- **Python: Attach to Docker Container** - Attach debugger to running container

### Tasks

Run tasks via `Terminal > Run Task...` or `Ctrl+Shift+P` > `Tasks: Run Task`:

- **Run Pytest - All Tests** (Default test task)
- **Run Pytest - Unit Tests**
- **Run Pytest - Integration Tests**
- **Run Pytest - E2E Tests**
- **Run Pytest with Coverage**
- **Format Code (Ruff + Black)**
- **Run Ruff Linter**
- **Run MyPy Type Checker**
- **Run Pre-commit Hooks**
- **Start Webhook Server (Local)**
- **Build Docker Image**
- **Run Docker Compose**

## Dev Container Setup

The project supports development in a Docker container:

### Using VS Code/Cursor

1. Install the "Dev Containers" extension
2. Open the project in VS Code/Cursor
3. Press `F1` and select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start
5. The environment will be automatically configured

### Dev Container Features

- Python 3.14 pre-installed
- All dependencies installed
- Git configured
- Docker-in-Docker support
- Pre-commit hooks installed
- Port forwarding for webhook server (59001) and debug (5678)

## Code Quality Tools

### Ruff - Modern Python Linter and Formatter

Ruff is the primary linter and formatter:

```bash
# Check code
make ruff

# Format code
make format

# Or use ruff directly
uv run ruff check .
uv run ruff format .
```

**Configuration**: `pyproject.toml` under `[tool.ruff]`

### Black - Code Formatter

Black is used alongside Ruff for consistent formatting:

```bash
# Check formatting
make black

# Format code
make format
```

**Configuration**: `pyproject.toml` under `[tool.black]`

### MyPy - Static Type Checker

MyPy enforces strict type checking:

```bash
# Run type checking
mypy .
```

**Configuration**: `pyproject.toml` under `[tool.mypy]`

**Important**: All functions must have complete type hints!

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Run manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

**Hooks configured:**
- Check YAML, JSON, TOML syntax
- Check for large files, private keys, merge conflicts
- Trim trailing whitespace
- Ruff linting and formatting
- Black formatting
- MyPy type checking
- Add trailing commas
- JIRA ticket integration

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=ondewo_nlu_webhook_server --cov-report=html

# Run specific test file
pytest tests/ondewo_nlu_webhook_server/server/test_server_unit.py

# Run specific test
pytest tests/ondewo_nlu_webhook_server/server/test_server_unit.py::test_server_connection
```

### Test Structure

```
tests/
├── __init__.py
├── e2e/                          # End-to-end tests
│   ├── conftest.py
│   └── test_webhook_server_e2e.py
├── ondewo_nlu_webhook_server/    # Unit/integration tests
│   ├── conftest.py
│   └── server/
│       └── test_server_unit.py
└── pytest_utils/                 # Test utilities
    ├── plugins/
    └── scripts/
```

### Writing Tests

Follow these guidelines:

```python
import pytest
from ondewo_nlu_webhook_server.server.base_models import WebhookRequest

@pytest.mark.unit
def test_webhook_request_validation() -> None:
    """Test that WebhookRequest validates input correctly."""
    # Arrange
    data = {
        "session": "projects/test/sessions/123",
        "query_text": "Hello",
        "intent": {"display_name": "test", "name": "test-id"}
    }

    # Act
    request = WebhookRequest(**data)

    # Assert
    assert request.session == data["session"]
    assert request.query_text == data["query_text"]
```

### Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Shows coverage summary
- **HTML**: `coverage/html/index.html` - Open in browser
- **XML**: `coverage/coverage.xml` - For CI/CD integration

View HTML coverage report:

```bash
# Generate and open coverage report
pytest --cov=ondewo_nlu_webhook_server --cov-report=html
open coverage/html/index.html  # macOS
xdg-open coverage/html/index.html  # Linux
start coverage/html/index.html  # Windows
```

## Git Workflow

### Commit Message Format

Use conventional commits with JIRA ticket:

```
[OND123-456] feat: add slot filling validation

- Add validation for context parameters
- Improve error messages
- Add unit tests for validation logic
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Branch Naming

```
feature/OND123-456_add-slot-filling-validation
bugfix/OND123-457_fix-context-handling
hotfix/OND123-458_critical-security-fix
```

### Pre-commit Workflow

1. Stage your changes: `git add .`
2. Commit: `git commit -m "[OND123-456] feat: your message"`
3. Pre-commit hooks run automatically
4. If hooks fail, fix issues and commit again
5. Push: `git push`

## Running the Webhook Server

### Local Development

```bash
# Run directly with Python
python -m ondewo_nlu_webhook_server.server.__main__

# Or use Make
make run_ondewo_nlu_webhook_server_release_in_container
```

### Docker Deployment

```bash
# Build and run with Docker Compose
make run_ondewo_nlu_webhook_server_release_in_container

# Run as daemon
make run_ondewo_nlu_webhook_server_release_in_container_daemon
```

### Environment Variables

Create a `.env` file or use `envs/local.env`:

```bash
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HOST=0.0.0.0
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_PORT=59001
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER=your-bearer-token
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME=admin
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD=secret
```

## Troubleshooting

### Test Discovery Not Working

1. Ensure pytest is installed: `uv pip install -e ".[dev]"`
2. Check Python interpreter in VS Code: `Ctrl+Shift+P` > "Python: Select Interpreter"
3. Reload window: `Ctrl+Shift+P` > "Developer: Reload Window"
4. Check test output: View > Output > Python Test Log

### Type Checking Errors

```bash
# Run MyPy to see all type errors
mypy .

# Check specific file
mypy ondewo_nlu_webhook_server/server/server.py
```

### Pre-commit Hooks Failing

```bash
# Run hooks manually to see detailed errors
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Import Errors

Ensure PYTHONPATH is set:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Or add to your shell profile:

```bash
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
source ~/.bashrc
```

### Docker Build Issues

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## Additional Resources

- [Project README](README.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Release Notes](RELEASE.md)
- [ONDEWO Documentation](https://ondewo.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pytest Documentation](https://docs.pytest.org)
- [Ruff Documentation](https://docs.astral.sh/ruff)
- [MyPy Documentation](https://mypy.readthedocs.io)

## Getting Help

If you encounter issues:

1. Check this development guide
2. Review the [CONTRIBUTING.md](CONTRIBUTING.md)
3. Search existing GitHub issues
4. Create a new issue with detailed information
5. Contact the ONDEWO team at office@ondewo.com
