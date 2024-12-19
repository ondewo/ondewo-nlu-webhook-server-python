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

import re
from typing import List

import setuptools

from ondewo_nlu_webhook_server.version import __version__


def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def read_requirements(file_path: str, encoding: str = 'utf-8') -> List[str]:
    with open(file_path, 'r', encoding=encoding) as f:
        requires = [
            re.sub(r'(.*)#egg=(.*)', r'\2 @ \1', line.strip())  # replace #egg= with @
            for line in f
            if line.strip() and not line.startswith('#')  # ignore empty lines and comments
        ]
    return requires


long_description: str = read_file('README.md')
requires: List[str] = read_requirements('requirements.txt')

setuptools.setup(
    name='ondewo-nlu-webhook-server',
    version=f'{__version__}',
    author='Ondewo GmbH',
    author_email='office@ondewo.com',
    description='ONDEWO NLU Webhook Server Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/ondewo/ondewo-nlu-webhook-server-python',
    packages=[package for package in setuptools.find_packages() if not package.startswith('test')],
    classifiers=[
        # Classifiers for releases https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=requires,
)
