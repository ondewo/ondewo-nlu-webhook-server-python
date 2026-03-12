# Python 3.14 Compatibility Guide

## Overview

This document describes the necessary steps to ensure compatibility with Python 3.14, which was released recently and doesn't have pre-built binary wheels for all packages yet.

## Issues with Python 3.14

Python 3.14 is very new, and many popular packages don't yet have pre-compiled binary wheels (`.whl` files) for this version. When you install these packages using the default method, you may get binary wheels that were compiled for older Python versions, which won't work with Python 3.14.

### Affected Packages

The following packages require compilation from source for Python 3.14:

1. **pydantic-core** - Core validation library for Pydantic
2. **grpcio** - gRPC framework for Python
3. **numpy** - Numerical computing library

## Solution: Build from Source

To fix this issue, these packages must be installed from source using the `--no-binary` flag with `uv pip`.

### Installation Commands

```bash
# Uninstall existing binary packages
uv pip uninstall pydantic pydantic-core grpcio grpcio-reflection grpcio-tools numpy

# Install with compilation from source
uv pip install --no-binary pydantic-core pydantic-core pydantic
uv pip install --no-binary grpcio grpcio grpcio-reflection grpcio-tools
uv pip install --no-binary numpy numpy
```

### Build Times

Building from source takes significantly longer than installing pre-built wheels:

- **pydantic-core**: ~4 minutes
- **grpcio**: ~8 minutes
- **numpy**: ~1.5 minutes

Total build time: ~13-15 minutes

## Automated Setup

The project's `Makefile` has been updated to handle this automatically. When running:

```bash
make setup_developer_environment_locally
```

The setup process will automatically build these packages from source if Python 3.14 is detected.

## Verification

After installation, verify that all packages work correctly:

```bash
# Test individual packages
python -c "import pydantic; print('pydantic works')"
python -c "import grpc; print('grpc works')"
python -c "import numpy; print('numpy works')"

# Test pytest discovery
pytest --collect-only

# Run unit tests
pytest tests/ondewo_nlu_webhook_server/ -v
```

## Expected Pytest Output

After fixing the compatibility issues, pytest should discover all tests:

```
collected 8 items

<Dir ondewo-nlu-webhook-server-python>
  <Package tests>
    <Package e2e>
      <Module test_webhook_server_e2e.py>
        <Class TestWebhookServerE2e>
          <Function test_server_connection>
          <Function test_custom_code[slot_filling]>
          <Function test_custom_code[response_refinement]>
    <Package ondewo_nlu_webhook_server>
      <Package server>
        <Module test_server_unit.py>
          <Function test_valid_request>
          <Function test_invalid_call_case>
          <Function test_invalid_json_format>
          <Function test_invalid_request_format>
          <Function test_custom_code_execution>
```

## Common Errors

### Error: `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`

**Cause**: Binary wheel for pydantic-core was built for an older Python version.

**Solution**: Reinstall pydantic-core from source:
```bash
uv pip uninstall pydantic pydantic-core
uv pip install --no-binary pydantic-core pydantic-core pydantic
```

### Error: `ImportError: cannot import name 'cygrpc' from 'grpc._cython'`

**Cause**: Binary wheel for grpcio was built for an older Python version.

**Solution**: Reinstall grpcio from source:
```bash
uv pip uninstall grpcio grpcio-reflection grpcio-tools
uv pip install --no-binary grpcio grpcio grpcio-reflection grpcio-tools
```

### Error: `ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'`

**Cause**: Binary wheel for numpy was built for an older Python version.

**Solution**: Reinstall numpy from source:
```bash
uv pip uninstall numpy
uv pip install --no-binary numpy numpy
```

## Future Considerations

As Python 3.14 becomes more widely adopted, package maintainers will publish pre-built wheels. At that point, the `--no-binary` flags can be removed, and installation will be faster.

Monitor these packages for Python 3.14 wheel availability:
- https://pypi.org/project/pydantic-core/#files
- https://pypi.org/project/grpcio/#files
- https://pypi.org/project/numpy/#files

## CI/CD Considerations

For CI/CD pipelines using Python 3.14:

1. **Increase timeout values**: Building from source takes longer than installing wheels
2. **Cache build artifacts**: Consider caching the built packages to speed up subsequent runs
3. **Use build dependencies**: Ensure build tools are available (gcc, g++, make, etc.)

### Required Build Dependencies

```bash
# Debian/Ubuntu
apt-get install -y build-essential python3-dev

# Alpine
apk add --no-cache gcc g++ make python3-dev

# RHEL/CentOS
yum install -y gcc gcc-c++ make python3-devel
```

## Docker Considerations

When building Docker images with Python 3.14:

1. Install build dependencies in the build stage
2. Build packages from source
3. Copy built packages to the runtime stage (multi-stage builds)
4. Remove build dependencies from the final image to keep it small

Example Dockerfile snippet:

```dockerfile
# Build stage
FROM python:3.14-slim AS builder
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN uv pip install --no-binary pydantic-core,grpcio,numpy -r requirements.txt

# Runtime stage
FROM python:3.14-slim
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
```

## Summary

Python 3.14 compatibility requires building certain packages from source due to the lack of pre-built wheels. This is a temporary situation that will improve as the Python ecosystem catches up with the new version. The project has been configured to handle this automatically, but developers should be aware of the longer installation times.
