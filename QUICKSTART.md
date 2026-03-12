# Quick Start Guide

Get up and running with ONDEWO NLU Webhook Server Python in minutes!

## Prerequisites

- Python 3.14+
- Git
- Docker (optional, for containerized development)

## 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/ondewo/ondewo-nlu-webhook-server-python.git
cd ondewo-nlu-webhook-server-python

# Run automated setup
make setup_developer_environment_locally
```

## 2. Verify Setup

```bash
# Run verification script
python scripts/verify_setup.py
```

This will check that all tools and configurations are properly installed.

## 3. Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ondewo_nlu_webhook_server --cov-report=html
```

## 5. Start the Server

### Local Development

```bash
# Start server locally
python -m ondewo_nlu_webhook_server.server.__main__
```

The server will be available at `http://localhost:59001`

### Docker

```bash
# Build and run with Docker Compose
make run_ondewo_nlu_webhook_server_release_in_container
```

The server will be available at `https://localhost:5678`

## VS Code / Cursor Setup

1. Open the project in VS Code or Cursor
2. Install recommended extensions (you'll be prompted)
3. Select Python interpreter: `Ctrl+Shift+P` > "Python: Select Interpreter" > `.venv`
4. Open Testing panel: Click beaker icon or `Ctrl+Shift+T`
5. Tests should automatically appear - click play to run!

## Common Commands

```bash
# Format code
make format

# Run linter
make ruff

# Run type checker
mypy .

# Run pre-commit hooks
pre-commit run --all-files

# Build Docker image
make build_server_image

# Create SSL certificates
make run_ondewo_nlu_webhook_server_create_ssl_certificates
```

## Project Structure

```
ondewo-nlu-webhook-server-python/
├── ondewo_nlu_webhook_server/          # Core server code
│   ├── server/                         # FastAPI server
│   │   ├── __main__.py                # Server entry point
│   │   ├── server.py                  # Route handlers
│   │   └── base_models.py             # Pydantic models
│   ├── constants.py                   # Constants
│   └── globals.py                     # Global configuration
├── ondewo_nlu_webhook_server_custom_integration/  # Custom logic
│   ├── custom_integration.py          # Main integration point
│   └── utils/                         # Utility functions
├── tests/                             # Test suite
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── e2e/                           # End-to-end tests
├── .vscode/                           # VS Code configuration
├── .devcontainer/                     # Dev container setup
├── pyproject.toml                     # Project configuration
└── Makefile                           # Build automation
```

## Adding Custom Code

Edit `ondewo_nlu_webhook_server_custom_integration/custom_integration.py`:

```python
from ondewo_nlu_webhook_server.server.base_models import Context, Intent

async def slot_filling(
    active_intent: Intent,
    active_contexts: list[Context] | None = None,
    headers: dict[str, str] | None = None,
) -> list[Context] | None:
    """
    Add your custom slot filling logic here.
    """
    # Your code here
    return active_contexts
```

## Environment Variables

Create `.env` file in project root:

```bash
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HOST=0.0.0.0
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_PORT=59001
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_BEARER=your-secret-token
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_USERNAME=admin
ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_HTTP_BASIC_AUTH_PASSWORD=secret
```

## Testing Your Changes

```bash
# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e              # End-to-end tests only

# Run specific test file
pytest tests/ondewo_nlu_webhook_server/server/test_server_unit.py

# Run with verbose output
pytest -v -s
```

## Code Quality

The project uses:

- **Ruff** - Fast Python linter and formatter
- **Black** - Code formatter
- **MyPy** - Static type checker
- **Pre-commit** - Git hooks for code quality

All code must:
- Have complete type hints
- Pass all linters
- Have 80%+ test coverage
- Follow PEP 8 style guide (120 char line length)

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/OND123-456_my-feature

# Make changes and commit
git add .
git commit -m "[OND123-456] feat: add my feature"

# Pre-commit hooks run automatically
# Push changes
git push origin feature/OND123-456_my-feature
```

## Troubleshooting

### Tests not discovered in VS Code

1. Reload window: `Ctrl+Shift+P` > "Developer: Reload Window"
2. Check Python interpreter is set to `.venv`
3. Check Output panel: View > Output > Python Test Log

### Import errors

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pre-commit hooks failing

```bash
# Run manually to see errors
pre-commit run --all-files

# Fix formatting
make format
```

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guide
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Check [.cursorrules](.cursorrules) for coding standards
- Explore example code in `ondewo_nlu_webhook_server_custom_integration/`

## Getting Help

- 📧 Email: office@ondewo.com
- 🐛 Issues: https://github.com/ondewo/ondewo-nlu-webhook-server-python/issues
- 📚 Docs: https://ondewo.com

Happy coding! 🚀
