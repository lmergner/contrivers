#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

with open('requirements.txt', 'r') as f:
    requires = f.readlines()

with open('test-requirements.txt', 'r') as f:
    tests_require = f.readlines()

setup(
    name='journal',
    version = '0.1dev',
    description='A Flask app with CMS.',
    long_description=readme + '\n\n' + history,
    author='Luke Thomas Mergner',
    author_email='lmergner@gmail.com',
    url='https://github.com/lmergner/journal',
    packages=[
        'journal',
    ],
    package_dir={'journal': 'journal'},
    include_package_data=True,
    install_requires=requires,
    license="BSD",
    zip_safe=False,
    keywords='journal',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=tests_require,
)
