#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import config

from core import (db, cache, login_manager)
from core.models import *
from core.app import ContriversFlask

from cms import cms, admin
from www import www
from cfg import SiteConfig


__version__ = "0.2"
__authors__ = ['Luke Thomas Mergner <lmergner@gmail.com']

__all__ = ['create_app']

default_blueprints = (
    www,
    cms,
)


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

    app = ContriversFlask(name, static_folder='static')

    @app.context_processor
    def site_settings():
        return dict(site=SiteConfig())

    # log to stderr
    import logging
    # from logging import StreamHandler
    if debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    # app.logger.addHandler(StreamHandler())

    if testing:
        app.logger.debug('Loading from TestConfig')
        app.config.from_object(config.TestConfig)
    else:
        app.logger.debug('Loading from ProductionConfig')
        app.config.from_object(config.ProductionConfig)

    app.config.update(additional_config_vars)

    # run ext.init_app(app) all in one place
    configure_ext(app)

    # Register our blueprints
    if blueprints is None:
        blueprints = default_blueprints
    for blueprint in blueprints:
        app.logger.debug('Registering blueprint {}'.format(blueprint.name))
        app.register_blueprint(blueprint)

    # Error handlers
    configure_error_handlers(app)

    if debug:
        app.logger.debug(app.url_map)
        for key, val in app.config.iteritems():
            if key != 'SECRET_KEY':
                app.logger.debug('{:<25} => {}'.format(key, val))
        app.logger.debug("App Static Path exists: {}".format(os.path.exists(app.static_folder)))
    return app


def configure_ext(app):
    """
    Load some Flask extensions. Note that this
    function is not dynamic.
    """

    # flask-sqlalchemy
    db.init_app(app)

    # flask-cache
    cache.init_app(app)

    # flask-login
    login_manager.init_app(app)

    # Flask-Admin
    admin.init_app(app)

    # Flask-Assets
    # assets.init_app(app)

    # Flask S3
    # s3.init_app(app)



def configure_error_handlers(app):
    pass


