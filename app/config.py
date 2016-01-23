#-*- coding: utf-8 -*-

import os


class Config(object):
    """Base flask app config object"""
    # DEFAULTS - these should be overwritten to false
    # unless explicitly set in app.create_app
    DEBUG = os.environ.get('CONTRIVERS_DEBUG', False)
    TESTING = os.environ.get('CONTRIVERS_TESTING', False)

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)

    # REDIS CACHE
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'contrivers-www'
    CACHE_DEFAULT_TIMEOUT = 60 * 15 # invalidate cache every 15 minutes

    # WTFORMS
    WTF_CSRF_ENABLED = True

    # AWS S3 - heroku only
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'null'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://')
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(16).encode('hex'))


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    CACHE_REDIS_URL = os.environ.get('REDISTOGO_URL', None)
