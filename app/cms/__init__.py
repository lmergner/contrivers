#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
app.cms

Authentication and management modules and blueprints.
"""

from flask import Blueprint
from .admin import admin

__all__ = ('cms', 'admin')

cms = Blueprint('cms', __name__, template_folder='./templates')
import views
