#!/usr/bin/env python
# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Verify that pytest discovery and execution work correctly.

This script checks:
1. Python version
2. Required packages are importable
3. Pytest can discover tests
4. Unit tests can run successfully
"""

import subprocess
import sys
from typing import Any


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """
    Run a shell command and return exit code, stdout, and stderr.

    Args:
        cmd: Command to run as a list of strings

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_python_version() -> bool:
    """Check Python version."""
    print("=" * 80)
    print("Checking Python version...")
    print("=" * 80)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor == 14:
        print("✅ Python 3.14 detected")
        print("⚠️  Note: Binary packages should be built from source for Python 3.14")
        return True
    elif version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Required: Python >= 3.10")
        return False


def check_package_imports() -> bool:
    """Check that required packages can be imported."""
    print("\n" + "=" * 80)
    print("Checking package imports...")
    print("=" * 80)

    packages = {
        "pydantic": "Pydantic (validation library)",
        "grpc": "gRPC (communication framework)",
        "numpy": "NumPy (numerical computing)",
        "fastapi": "FastAPI (web framework)",
        "pytest": "Pytest (testing framework)",
    }

    all_ok = True
    for package, description in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {description}: {version}")
        except ImportError as e:
            print(f"❌ {description}: Import failed - {e}")
            all_ok = False

    return all_ok


def check_pytest_discovery() -> bool:
    """Check that pytest can discover tests."""
    print("\n" + "=" * 80)
    print("Checking pytest test discovery...")
    print("=" * 80)

    exit_code, stdout, stderr = run_command(["pytest", "--collect-only", "-q"])

    if exit_code != 0:
        print("❌ Pytest discovery failed")
        print(f"Exit code: {exit_code}")
        print(f"Stderr: {stderr}")
        return False

    # Count collected tests
    if "collected" in stdout:
        for line in stdout.split("\n"):
            if "collected" in line:
                print(f"✅ {line.strip()}")
                break
        return True
    else:
        print("❌ No tests were collected")
        return False


def run_unit_tests() -> bool:
    """Run unit tests."""
    print("\n" + "=" * 80)
    print("Running unit tests...")
    print("=" * 80)

    exit_code, stdout, stderr = run_command(["pytest", "tests/ondewo_nlu_webhook_server/", "-v", "--tb=short", "-q"])

    if exit_code != 0:
        print("❌ Unit tests failed")
        print(f"Exit code: {exit_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

    # Check for passed tests
    if "passed" in stdout:
        for line in stdout.split("\n"):
            if "passed" in line:
                print(f"✅ {line.strip()}")
                break
        return True
    else:
        print("❌ No tests passed")
        return False


def main() -> int:
    """
    Main verification function.

    Returns:
        Exit code: 0 if all checks pass, 1 otherwise
    """
    print("\n" + "=" * 80)
    print("ONDEWO NLU Webhook Server - Pytest Verification")
    print("=" * 80)

    checks: dict[str, Any] = {
        "Python Version": check_python_version,
        "Package Imports": check_package_imports,
        "Pytest Discovery": check_pytest_discovery,
        "Unit Tests": run_unit_tests,
    }

    results: dict[str, bool] = {}

    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name} check failed with exception: {e}")
            results[check_name] = False

    # Print summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All checks passed! Pytest is working correctly.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        print("\nFor Python 3.14 compatibility issues, see:")
        print("  - PYTHON_3.14_COMPATIBILITY.md")
        print("  - PYTEST_FIX_SUMMARY.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
