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

import os
import re
from typing import List

from Cython.Build import cythonize
from setuptools import (
    Extension,
    find_packages,
    setup,
)

from ondewo_nlu_webhook_server.version import __version__

extensions = cythonize(
    [
        Extension(
            "ondewo_nlu_webhook_server.*",
            ["ondewo_nlu_webhook_server/**/*.py"],
        ),
        Extension(
            "ondewo_nlu_webhook_server_custom_integration.*",
            ["ondewo_nlu_webhook_server_custom_integration/**/*.py"],
        ),
    ],
    language_level=3,
)


def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def read_requirements(file_path: str, encoding: str = 'utf-8') -> List[str]:
    def _parse_requirements(path: str, seen_files: set) -> List[str]:
        requirements = []
        with open(path, 'r', encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):  # Ignore empty lines and comments
                    continue

                # Handle recursive requirements
                if line.startswith('-r'):
                    nested_file = line.split(maxsplit=1)[1]
                    nested_path = os.path.join(os.path.dirname(path), nested_file)
                    if nested_path in seen_files:
                        raise ValueError(f"Circular reference detected with {nested_path}")
                    seen_files.add(nested_path)
                    requirements.extend(_parse_requirements(nested_path, seen_files))
                else:
                    # Replace #egg= with @ and add to requirements
                    requirements.append(re.sub(r'(.*)#egg=(.*)', r'\2 @ \1', line))
        return requirements

    return _parse_requirements(file_path, seen_files=set())


long_description: str = read_file('README.md')
requires: List[str] = read_requirements('requirements.txt')

setup(
    name='ondewo-nlu-webhook-server',
    version=f'{__version__}',
    author='Ondewo GmbH',
    author_email='office@ondewo.com',
    description='ONDEWO NLU Webhook Server Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ondewo/ondewo-nlu-webhook-server-python',
    packages=[package for package in find_packages() if not package.startswith('test')],
    ext_modules=cythonize(
        extensions,
        language_level=3,
        nthreads=os.cpu_count(),
    ),
    install_requires=requires,
    python_requires='>=3.10',
    classifiers=[
        # Classifiers for releases https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
)
