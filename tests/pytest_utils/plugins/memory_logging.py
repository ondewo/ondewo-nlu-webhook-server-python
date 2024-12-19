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
This pytest-plugin can be enabled by adding an entry to the pytest_plugins list in conftest.py:
pytest_plugins = [..., 'pytest_utils.plugins.memory_logging', ...]

If enabled, it prints a list of all tests which leak more than 10MB of RAM in the pytest console report.
Leakage is measured as the difference of RAM-consumption before and after the test run.

Current shortcomings:
- will print a " failure in leak calculations " warning for tests which are skipped;
(this is probably because pytest_runtest_setup is run for all tests, including skipped ones,
while pytest_runtest_teardown apparently only runs for tests which have been run)

From https://nvbn.github.io/2017/02/02/pytest-leaking/
"""
import os
from collections import namedtuple
from itertools import groupby
from operator import attrgetter
from typing import Any

from _pytest.nodes import Item
from psutil import Process

LEAK_LIMIT = 10 * 1024 * 1024  # report memory leaks larger than 10MB

_proc = Process(os.getpid())

ConsumedRamLogEntry = namedtuple('ConsumedRamLogEntry', ('nodeid', 'on', 'consumed_ram'))
consumed_ram_log = []


def add_consumed_ram_entry(item: Item, on: str) -> None:
    log_entry = ConsumedRamLogEntry(item.nodeid, on, get_consumed_ram())
    consumed_ram_log.append(log_entry)


def get_consumed_ram() -> Any:
    return _proc.memory_info().rss


def pytest_runtest_setup(item: Item) -> None:
    add_consumed_ram_entry(item, on='START')


def pytest_runtest_teardown(item: Item) -> None:
    add_consumed_ram_entry(item, on='END')


def pytest_terminal_summary(terminalreporter: Any) -> None:
    grouped = groupby(consumed_ram_log, lambda entry: entry.nodeid)  # type: ignore

    leaked_message = ''
    leaked_failure_message = ''
    for nodeid, entries in grouped:
        try:
            start_entry, end_entry = entries
            leaked = end_entry.consumed_ram - start_entry.consumed_ram
            if leaked > LEAK_LIMIT:
                leaked_message = leaked_message + f'LEAKED {(leaked / 1024 / 1024):.1f}MB in {nodeid}\n'
        except ValueError:
            leaked_failure_message = leaked_failure_message + f'{nodeid}\n'

    if leaked_failure_message:
        terminalreporter.write_sep(sep="=", title="failure in leak calculations")
        terminalreporter.write(leaked_failure_message)

    if leaked_message:
        terminalreporter.write_sep(sep="=", title="leakages")
        terminalreporter.write(leaked_message)

    if consumed_ram_log:
        max_mem_use = sorted(consumed_ram_log, key=attrgetter('consumed_ram'))[-1]
        if max_mem_use:
            terminalreporter.write_sep(sep="=", title="maximum memory usage")
            terminalreporter.write(
                f'{max_mem_use.consumed_ram / 1024 / 1024:.1f}MB'
                f' on {max_mem_use.on} of {max_mem_use.nodeid}\n'
            )
