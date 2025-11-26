# Quick Reference - Pytest and Python 3.14

## ✅ Status: All Fixed

Pytest discovery and execution are now fully working with Python 3.14.

## Quick Commands

```bash
# Verify everything works
python scripts/verify_pytest.py

# Discover tests
pytest --collect-only

# Run unit tests
pytest tests/ondewo_nlu_webhook_server/ -v

# Run all tests (excluding e2e which needs Docker)
pytest tests/ondewo_nlu_webhook_server/ -v

# Run with coverage
pytest tests/ondewo_nlu_webhook_server/ --cov
```

## Test Results

✅ **8 tests discovered**
- 3 E2E tests (require Docker)
- 5 Unit tests (all passing)

✅ **All unit tests passing**
```
test_valid_request ............................ PASSED
test_invalid_call_case ........................ PASSED
test_invalid_json_format ...................... PASSED
test_invalid_request_format ................... PASSED
test_custom_code_execution .................... PASSED
```

## Python 3.14 Compatibility

### Issue
Binary packages (pydantic-core, grpcio, numpy) didn't have pre-built wheels for Python 3.14.

### Solution
Rebuilt from source automatically via Makefile:
```bash
make setup_developer_environment_locally
```

### Manual Fix (if needed)
```bash
make fix_python_314_compatibility
```

## Package Versions

| Package | Version | Status |
|---------|---------|--------|
| Python | 3.14.0 | ✅ |
| pytest | 9.0.1 | ✅ |
| pydantic | 2.12.5 | ✅ |
| grpcio | 1.76.0 | ✅ |
| numpy | 2.3.5 | ✅ |
| fastapi | 0.122.0 | ✅ |

## Documentation

- **PYTHON_3.14_COMPATIBILITY.md** - Detailed compatibility guide
- **PYTEST_FIX_SUMMARY.md** - Fix summary and verification
- **PYTEST_DISCOVERY_FIX_COMPLETE.md** - Complete report
- **QUICKSTART.md** - Get started in 5 minutes
- **DEVELOPMENT.md** - Comprehensive development guide

## Troubleshooting

### Import Error: pydantic_core._pydantic_core
```bash
uv pip uninstall pydantic pydantic-core
uv pip install --no-binary pydantic-core pydantic-core pydantic
```

### Import Error: grpc._cython.cygrpc
```bash
uv pip uninstall grpcio grpcio-reflection grpcio-tools
uv pip install --no-binary grpcio grpcio grpcio-reflection grpcio-tools
```

### Import Error: numpy._core._multiarray_umath
```bash
uv pip uninstall numpy
uv pip install --no-binary numpy numpy
```

### All-in-one Fix
```bash
make fix_python_314_compatibility
```

## VS Code / Cursor

Test discovery and execution work automatically in VS Code/Cursor:

1. Open Testing panel (beaker icon)
2. Tests auto-discover
3. Click play button to run
4. Debug tests with breakpoints

## CI/CD Notes

- Build time: ~15 minutes (due to source compilation)
- Cache built packages to speed up subsequent runs
- Ensure build dependencies are available (gcc, g++, make)

## Known Warnings (Non-blocking)

- Pydantic v2 migration warnings (to be addressed separately)
- Coverage "no data collected" during collection (expected)
- httpx content parameter deprecation

## Need Help?

1. Run verification: `python scripts/verify_pytest.py`
2. Check documentation: `PYTHON_3.14_COMPATIBILITY.md`
3. Review test output: `pytest -v`

---

**Last Updated**: 2025-11-26
**Status**: ✅ All systems operational
