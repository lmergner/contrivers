#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    frontend.ext
    ------------

    Import extensions here to avoid circular imports.
"""

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

# from sqlalchemy.ext.declarative import declarative_base
# from flask.ext.sqlalchemy import SQLAlchemy, _QueryProperty, _BoundDeclarativeMeta, Model

# class SQLA(SQLAlchemy):
#     """ Subclass Flask-SQLAlchemy to monkeypatch the declarative_base class """

#     def __init__(self, *args, **kwargs):
#         self.base_model = kwargs.pop('base_model', Model)
#         super(SQLA, self).__init__(*args, **kwargs)

#     def make_declarative_base(self, metadata=None):
#         """Creates the declarative base."""
#         base = declarative_base(
#             cls=self.base_model, name='Model',
#             metadata=metadata,
#             metaclass=_BoundDeclarativeMeta)
#         base.query = _QueryProperty(self)
#         return base

# from .meta import Base
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()
