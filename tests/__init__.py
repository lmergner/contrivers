# -*- coding: utf-8 -*-

import subprocess
import shlex
from app import db

# Nosetest package setup method
def setUp():
    subprocess.check_call(shlex.split('dropdb contrivers-unittests --if-exists'))
    subprocess.check_call(shlex.split('createdb -O contrivers contrivers-unittests'))

def tearDown():
    pass
