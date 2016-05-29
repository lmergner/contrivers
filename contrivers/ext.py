#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    contrivers.ext
    ------------

    Import extensions here to avoid circular imports.
"""

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

# from flask_s3 import FlaskS3
# s3 = FlaskS3()
