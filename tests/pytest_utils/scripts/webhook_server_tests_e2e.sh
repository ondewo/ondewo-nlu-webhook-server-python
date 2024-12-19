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

#!/usr/bin/env bash
export PYTHONPATH=/opt/ondewo-nlu-webhook-server-python

# Escape $1 for safe usage in filenames
escaped_arg_1=$(echo "$1" | sed 's/[^a-zA-Z0-9]/_/g')

# general pytest options
args="-v"
args="$args  -rfE"
args="$args --capture=tee-sys"
args="$args --show-capture=all"
args="$args --durations=30"
args="$args --tb=long"
args="$args --color=yes"
args="$args --cov"
args="$args --cov-append"

# rerun failed tests x times with a delay of y
args="$args --reruns 1"
args="$args --reruns-delay 5"

# xdist
#args="$args --debug"
args="$args --dist=loadscope"
#args="$args --dist=worksteal"
args="$args -d --tx popen//python=python3.12"

# specific pytest options
args="$args --cov-report xml:coverage/coverage-${escaped_arg_1}.xml"
args="$args --junit-xml=junit/pytest_e2e-${escaped_arg_1}.xml"
args="$args -n 1"

echo "START: ------------------------- PYTEST ARGS --------------------------"
echo "pytest $args $1"
echo "DONE: ------------------------- PYTEST ARGS --------------------------"

echo "START: ------------------------- ls -l  --------------------------"
ls -l
ls -l tests
echo "DONE: ------------------------- ls -l --------------------------"

pytest $args "$1"
