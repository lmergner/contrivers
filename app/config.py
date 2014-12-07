#-*- coding: utf-8 -*-

import os


class Config(object):
    """Base flask app config object"""
    DEBUG = os.environ.get('DEBUG', False)
    TESTING = os.environ.get('TESTING', False)
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'contrivers-review'
    CACHE_DEFAULT_TIMEOUT = 60 * 15 # invalidate cache every 15 minutes
    MOBILE_COOKIE = 'mobile'
    S3_BUCKET_NAME = 'contrivers-assets'
    USE_S3 = True


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'null'
    CACHE_REDIS_URL = 'redis://'
    SQLALCHEMY_DATABASE_URI = 'postgres://contrivers@localhost/contrivers'
    SECRET_KEY = os.urandom(16).encode('hex')
    S3_BUCKET_NAME = 'contrivers-staging'
    USE_S3_DEBUG = True
    FLASK_ASSETS_USE_S3 = False
    ASSETS_DEBUG = True


class ProductionConfig(Config):
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', None)
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', None)
    CACHE_REDIS_URL = os.environ.get('REDISTOGO_URL', None)
    FLASK_ASSETS_USE_S3 = True
