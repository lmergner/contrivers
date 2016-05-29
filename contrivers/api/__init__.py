#!/usr/bin/env python
#-*- coding: utf-8
"""
    app.api
    -------

    Provide json endpoints for CRUD
"""

from flask import Blueprint

from .views import api_view_factory
from ..core.models import __models__ as core_models


api = Blueprint('api', __name__, url_prefix='/api')
api_view_factory(api, core_models)

@api.after_app_request
def add_headers(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r
