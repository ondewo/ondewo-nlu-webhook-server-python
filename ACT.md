# Running GitHub Actions Locally with `act`

This guide explains how to run GitHub Actions workflows locally using [`act`](https://github.com/nektos/act).

## Prerequisites

1. **Docker** must be installed and running
2. **act** tool must be installed

### Installing act

```bash
# Install act using the official installer
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Or using package managers:
# macOS (Homebrew)
brew install act

# Linux (using the installer script)
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Configuring act

After installation, configure `act` to use a default runner image:

```bash
# Create config directory
mkdir -p ~/.config/act

# Configure to use medium image (recommended)
echo "-P ubuntu-latest=catthehacker/ubuntu:act-latest" > ~/.config/act/actrc
```

This configuration uses the medium-sized image which includes necessary tools and is compatible with most actions.

## Quick Start

### Using the Helper Script

The easiest way to run the workflow locally is using the provided helper script:

```bash
# Run all jobs
./scripts/run-github-actions-locally.sh

# Run a specific job
./scripts/run-github-actions-locally.sh --job code-style
./scripts/run-github-actions-locally.sh --job unit-tests
./scripts/run-github-actions-locally.sh --job e2e-tests

# List available jobs
./scripts/run-github-actions-locally.sh --list

# Dry run (see what would be executed)
./scripts/run-github-actions-locally.sh --dry-run
```

### Using act Directly

You can also use `act` directly:

```bash
# Run all jobs in the workflow
act -W .github/workflows/unit-tests.yml

# Run a specific job
act -W .github/workflows/unit-tests.yml -j code-style
act -W .github/workflows/unit-tests.yml -j unit-tests
act -W .github/workflows/unit-tests.yml -j e2e-tests

# List all jobs
act -W .github/workflows/unit-tests.yml --list

# Dry run
act -W .github/workflows/unit-tests.yml --dryrun
```

## Available Jobs

The workflow contains three jobs that run sequentially:

1. **`code-style`** - Runs code style checks:
   - `ruff check .` - Linting
   - `ruff format --check .` - Format check
   - `black --check .` - Format check

2. **`unit-tests`** - Runs unit and integration tests (runs after code-style passes)

3. **`e2e-tests`** - Runs end-to-end tests (runs after unit-tests passes)

## Notes

- **Docker Services**: The workflow uses Docker services (docker:dind). `act` handles these automatically, but make sure Docker is running on your machine.

- **Environment Variables**: The workflow sources `envs/local.env` for environment variables. Make sure this file exists and contains the necessary configuration.

- **Performance**: Running workflows locally can be slower than on GitHub Actions, especially for jobs that require Docker services.

- **Limitations**: Some GitHub Actions features may not work exactly the same locally as they do on GitHub. If you encounter issues, check the [act documentation](https://github.com/nektos/act).

## Troubleshooting

### Docker not running
```bash
# Check if Docker is running
docker ps

# Start Docker if needed (varies by system)
sudo systemctl start docker  # Linux
# or start Docker Desktop on macOS/Windows
```

### act not found
```bash
# Check if act is installed
which act

# If not found, install it
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Permission issues
```bash
# Make sure the script is executable
chmod +x scripts/run-github-actions-locally.sh
```

## Additional Resources

- [act GitHub Repository](https://github.com/nektos/act)
- [act Documentation](https://github.com/nektos/act#readme)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
