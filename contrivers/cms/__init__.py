#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
app.cms

Authentication and management modules and blueprints.
"""

import os

from flask import Blueprint, current_app
from .admin import admin

__all__ = ('cms', 'admin')

absolute_template_path = os.path.join(os.path.dirname(__file__), 'templates')

cms = Blueprint('cms', __name__,
        template_folder=absolute_template_path,
        static_folder='static',
        url_prefix='/cms'
        )

import views
