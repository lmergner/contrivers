#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    contrivers.www
    -------

"""

from flask import Blueprint


__all__ = ('www')

www = Blueprint(
    'www', __name__,
    template_folder='../templates',
    # static_url_path='',
    static_folder='static')

from . import views as views
from . import jinja_helpers as jinja_helpers
