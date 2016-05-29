#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('requirements.txt', 'r') as f:
    REQUIRE = f.readlines()

with open('dev-requirements.txt', 'r') as f:
    TESTS_REQUIRE = f.readlines()

setup(
    name='contrivers',
    version='0.2.1',
    description='a publishing engine for www.contrivers.org',
    author='Luke Thomas Mergner',
    author_email='lmergner@gmail.com',
    url='https://github.com/lmergner/contrivers',
    packages=[
        'app',
    ],
    include_package_data=True,
    install_requires=REQUIRE,
    license="MIT",
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=TESTS_REQUIRE,
)
