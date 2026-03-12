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

import glob
import os

from Cython.Build import cythonize
from setuptools import Extension, setup


def make_extensions(base_dir: str) -> list[Extension]:
    """Create Cython Extension objects for all .py files, excluding __main__.py.

    __main__.py files must remain as plain Python source because
    'python -m package' cannot execute compiled .so entry points.
    """
    extensions: list[Extension] = []
    for filepath in sorted(glob.glob(f"{base_dir}/**/*.py", recursive=True)):
        if filepath.endswith("__main__.py"):
            continue
        # Convert file path to dotted module name: a/b/c.py -> a.b.c
        module_name: str = filepath.replace(os.sep, ".").removesuffix(".py")
        extensions.append(Extension(module_name, [filepath]))
    return extensions


# Cython extensions configuration
# Most project metadata is now in pyproject.toml
extensions: list[Extension] = cythonize(
    make_extensions("ondewo_nlu_webhook_server") + make_extensions("ondewo_nlu_webhook_server_custom_integration"),
    language_level=3,
    nthreads=os.cpu_count(),
)

# Version is read dynamically from pyproject.toml via tool.setuptools.dynamic
setup(
    ext_modules=extensions,
)
