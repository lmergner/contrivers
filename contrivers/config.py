#-*- coding: utf-8 -*-

import os
import codecs


class Config(object):
    """Base flask app config object"""
    # DEFAULTS - these should be overwritten to false
    # unless explicitly set in app.create_app
    TITLE = 'Contrivers\' Review'
    TAGLINE = 'Theory, Politics, Criticism'
    TWITTER_NAME = 'contriversrev'
    AMZN_TAG = 'contrivers-review-20'
    DEBUG = os.environ.get('CONTRIVERS_DEBUG', False)
    TESTING = os.environ.get('CONTRIVERS_TESTING', False)
    BUCKET = os.environ.get('S3_BUCKET_NAME', 'contrivers-assets')

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # REDIS CACHE
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://')
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'contrivers-www'
    CACHE_DEFAULT_TIMEOUT = 60 * 15 # invalidate cache every 15 minutes

    # WTFORMS
    WTF_CSRF_ENABLED = True

    # AWS S3 - heroku only
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)


class TestConfig(Config):
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False
    TESTING = True
    CACHE_TYPE = 'null'
    SECRET_KEY = os.environ.get('SECRET_KEY', codecs.encode(os.urandom(64), 'hex').decode())
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgres://contrivers@localhost/contrivers-develop')

class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', None)
