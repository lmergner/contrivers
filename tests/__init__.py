# -*- coding: utf-8 -*-

import subprocess
import shlex

# Nosetest pre/post test fixtures

def setUp():
    subprocess.check_call(shlex.split('dropdb contrivers-unittests --if-exists'))
    subprocess.check_call(shlex.split('createdb -O contrivers contrivers-unittests'))

def tearDown():
    pass


