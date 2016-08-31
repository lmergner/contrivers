#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
contrivers
----------

defines create_app factory function and performs setup for the application.
"""

import os
import config
import importlib
from datetime import datetime
from flask import Flask

from .ext import db

__version__ = "0.3.0"
__authors__ = ['Luke Thomas Mergner <lmergner@gmail.com']

__all__ = ['create_app']

default_blueprints = ( 'www',)
default_extensions = ()


def create_app(
    name='contrivers-review', testing=False,
    debug=False, blueprints=None, additional_config_vars={}):
    """
    Application Factory

    :param name: The app-name
    :param testing: Boolean to load the testing config.
    :param debug: Boolean to turn on some debug messages
    :param blueprints: If None load default blueprints, pass an
    empty list to disable blueprints.
    :param additional_config_vars: A dictionary of optional config vars
    that are loaded *after* the app is configured from files.
    :returns: Flask app object.

    Configuration Order:
        1. From the config files in ./config.py
        3. Via a dictionary keyword

    The function then loads extensions defined in `configure_ext`, loads
    the blueprints, registers some jinja helpers and error handling before
    returning the app object.

    """

    app = Flask(name, static_folder='static')

    # log to stderr
    import logging
    # from logging import StreamHandler
    if debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    # app.logger.addHandler(StreamHandler())

    # Load the appropriate config based on an environmental variable
    if testing:
        app.config.from_object(config.TestConfig)
    else:
        app.config.from_object(config.ProductionConfig)

    # Update the config with any cli args
    app.config.update(additional_config_vars)

    for key in sorted(app.config.keys()):
        print('{} => {}'.format(key, app.config.get(key)))

    # run ext.init_app(app) all in one place
    configure_ext(app)

    # Register our blueprints
    if blueprints is None:
        blueprints = default_blueprints

    for blueprint_str in blueprints:
        blueprint = getattr(importlib.import_module('contrivers.' + blueprint_str), blueprint_str)
        app.logger.debug('Registering blueprint {}'.format(blueprint.name))
        app.register_blueprint(blueprint)

    # Error handlers
    configure_error_handlers(app)

    @app.context_processor
    def context():
        return dict(year=str(datetime.today().year))

    return app


def configure_ext(app):
    """ Load some Flask extensions """

    # flask-sqlalchemy
    db.init_app(app)


def configure_error_handlers(app):
    # TODO: configure error handlers
    pass
