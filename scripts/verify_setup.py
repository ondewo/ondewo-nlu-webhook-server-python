#!/usr/bin/env python3
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
Verify development environment setup.

This script checks that all required tools and configurations are properly set up
for development on the ONDEWO NLU Webhook Server Python project.
"""

import subprocess
import sys
from pathlib import Path


def check_command(command: str, version_arg: str = "--version") -> tuple[bool, str]:
    """
    Check if a command is available and get its version.

    Args:
        command: Command to check
        version_arg: Argument to get version (default: --version)

    Returns:
        Tuple of (success, version_string)
    """
    try:
        result = subprocess.run(
            [command, version_arg],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            return True, version.split("\n")[0]
        return False, "Command failed"
    except FileNotFoundError:
        return False, "Not found"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_file(filepath: Path) -> bool:
    """
    Check if a file exists.

    Args:
        filepath: Path to file

    Returns:
        True if file exists
    """
    return filepath.exists()


def print_status(name: str, success: bool, details: str = "") -> None:
    """
    Print status of a check.

    Args:
        name: Name of the check
        success: Whether check passed
        details: Additional details
    """
    status = "✅" if success else "❌"
    print(f"{status} {name:<30} {details}")


def main() -> int:
    """
    Run all verification checks.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 80)
    print("ONDEWO NLU Webhook Server Python - Development Environment Verification")
    print("=" * 80)
    print()

    project_root = Path(__file__).parent.parent
    all_passed = True

    # Check Python
    print("Python Environment:")
    print("-" * 80)
    success, version = check_command("python3", "--version")
    print_status("Python 3", success, version)
    if not success:
        all_passed = False

    success, version = check_command("python3.14", "--version")
    print_status("Python 3.14", success, version if success else "Not found (required)")
    if not success:
        all_passed = False

    print()

    # Check Package Managers
    print("Package Managers:")
    print("-" * 80)
    success, version = check_command("uv", "--version")
    print_status("uv", success, version if success else "Not found (recommended)")
    if not success:
        print("  ℹ️  Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")

    success, version = check_command("pip", "--version")
    print_status("pip", success, version)
    if not success:
        all_passed = False

    print()

    # Check Development Tools
    print("Development Tools:")
    print("-" * 80)
    success, version = check_command("git", "--version")
    print_status("git", success, version)
    if not success:
        all_passed = False

    success, version = check_command("docker", "--version")
    print_status("docker", success, version if success else "Not found (optional)")

    success, version = check_command("docker-compose", "--version")
    print_status("docker-compose", success, version if success else "Not found (optional)")

    success, version = check_command("make", "--version")
    print_status("make", success, version)
    if not success:
        all_passed = False

    print()

    # Check Python Tools
    print("Python Development Tools:")
    print("-" * 80)
    success, version = check_command("ruff", "--version")
    print_status("ruff", success, version if success else "Not installed")
    if not success:
        all_passed = False

    success, version = check_command("black", "--version")
    print_status("black", success, version if success else "Not installed")
    if not success:
        all_passed = False

    success, version = check_command("mypy", "--version")
    print_status("mypy", success, version if success else "Not installed")
    if not success:
        all_passed = False

    success, version = check_command("pytest", "--version")
    print_status("pytest", success, version if success else "Not installed")
    if not success:
        all_passed = False

    success, version = check_command("pre-commit", "--version")
    print_status("pre-commit", success, version if success else "Not installed")
    if not success:
        all_passed = False

    print()

    # Check Configuration Files
    print("Configuration Files:")
    print("-" * 80)
    config_files = [
        "pyproject.toml",
        ".pre-commit-config.yaml",
        ".editorconfig",
        ".cursorrules",
        ".vscode/settings.json",
        ".vscode/launch.json",
        ".vscode/tasks.json",
        ".vscode/extensions.json",
        ".devcontainer/devcontainer.json",
        ".gitignore",
    ]

    for config_file in config_files:
        filepath = project_root / config_file
        success = check_file(filepath)
        print_status(config_file, success)
        if not success:
            all_passed = False

    print()

    # Check Project Structure
    print("Project Structure:")
    print("-" * 80)
    required_dirs = [
        "ondewo_nlu_webhook_server",
        "ondewo_nlu_webhook_server_custom_integration",
        "tests",
        "scripts",
    ]

    for directory in required_dirs:
        dirpath = project_root / directory
        success = check_file(dirpath)
        print_status(directory, success)
        if not success:
            all_passed = False

    print()

    # Check Virtual Environment
    print("Virtual Environment:")
    print("-" * 80)
    venv_path = project_root / ".venv"
    success = check_file(venv_path)
    print_status(".venv directory", success, "Found" if success else "Not found")
    if not success:
        print("  ℹ️  Create venv: python3.14 -m venv .venv")
        print("  ℹ️  Activate: source .venv/bin/activate")

    print()

    # Summary
    print("=" * 80)
    if all_passed:
        print("✅ All checks passed! Your development environment is ready.")
        print()
        print("Next steps:")
        print("  1. Activate virtual environment: source .venv/bin/activate")
        print("  2. Install dependencies: make setup_developer_environment_locally")
        print("  3. Run tests: pytest")
        print("  4. Start coding! 🚀")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        print()
        print("To fix issues:")
        print("  1. Install missing tools")
        print("  2. Run: make setup_developer_environment_locally")
        print("  3. Run this script again: python scripts/verify_setup.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
