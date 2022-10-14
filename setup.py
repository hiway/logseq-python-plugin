#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function
)

import io
import re
from glob import glob
from os.path import (
    basename,
    dirname,
    join,
    splitext
)

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='logspyq',
    version='0.1.0',
    license='MIT',
    description='Python-for-Logseq Plugins',
    author='Harshad Sharma',
    author_email='harshad@sharma.io',
    url='https://github.com/hiway/logspyq',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    keywords=[
    ],
    install_requires=[
        'apscheduler',
        'click',
        'keyvalue-sqlite==1.0.5',
        'python-box',
        'python-socketio',
        'quart',
        'quart-cors',
        'uvicorn[standard]',
        'uvloop',
    ],
    dev_requires=[
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-mock',
    ],
    entry_points={
        'console_scripts': [
            'logspyq = logspyq.server.cli:main',
        ]
    },
)
