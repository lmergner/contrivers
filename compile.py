#!/usr/bin/env python

import sass
import os

print('Compiling sass files.')

os.makedirs('./assets/css', exist_ok=True)
sass.compile(dirname=('styles', 'assets/css'))
