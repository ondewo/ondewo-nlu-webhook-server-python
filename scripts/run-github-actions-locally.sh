#!/usr/bin/env bash
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

# Script to run GitHub Actions workflow locally using act
# See: https://github.com/nektos/act

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find act binary
ACT_BIN=""
if command -v act > /dev/null 2>&1; then
    ACT_BIN="act"
elif [ -f "./bin/act" ]; then
    ACT_BIN="./bin/act"
elif [ -f "$HOME/.local/bin/act" ]; then
    ACT_BIN="$HOME/.local/bin/act"
else
    echo -e "${RED}Error: act not found. Please install act first:${NC}"
    echo "  curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    exit 1
fi

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Get the workflow file
WORKFLOW_FILE=".github/workflows/unit-tests.yml"
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo -e "${RED}Error: Workflow file not found: $WORKFLOW_FILE${NC}"
    exit 1
fi

# Parse command line arguments
JOB_NAME=""
LIST_JOBS=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --job)
            JOB_NAME="$2"
            shift 2
            ;;
        --list)
            LIST_JOBS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --job JOB_NAME    Run a specific job (code-style, unit-tests, e2e-tests)"
            echo "  --list            List all available jobs"
            echo "  --dry-run         Show what would be executed without running"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Run all jobs"
            echo "  $0 --job code-style     # Run only code style checks"
            echo "  $0 --job unit-tests     # Run only unit tests"
            echo "  $0 --job e2e-tests      # Run only e2e tests"
            echo "  $0 --list               # List all jobs"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# List jobs if requested
if [ "$LIST_JOBS" = true ]; then
    echo -e "${GREEN}Available jobs in the workflow:${NC}"
    echo "  - code-style: Run ruff and black code style checks"
    echo "  - unit-tests: Run unit and integration tests"
    echo "  - e2e-tests: Run end-to-end tests"
    exit 0
fi

# Build act command
ACT_CMD="$ACT_BIN -W $WORKFLOW_FILE"

if [ -n "$JOB_NAME" ]; then
    ACT_CMD="$ACT_CMD -j $JOB_NAME"
    echo -e "${YELLOW}Running job: $JOB_NAME${NC}"
else
    echo -e "${YELLOW}Running all jobs in the workflow${NC}"
fi

# Add dry-run flag if requested
if [ "$DRY_RUN" = true ]; then
    ACT_CMD="$ACT_CMD --dryrun"
    echo -e "${YELLOW}Dry-run mode: showing what would be executed${NC}"
fi

# Run act
echo -e "${GREEN}Executing: $ACT_CMD${NC}"
echo ""

$ACT_CMD

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Workflow completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Workflow failed with exit code: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
