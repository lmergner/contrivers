# -*- coding: utf-8 -*-
"""
    tests/test_assets

    We don't care if the asset can be loaded (i.e. 200 or 404).
    Instead, we care if the template prints the expected url
    when the testing flag is set (local) or unset (s3).
"""

import pytest
from flask import url_for
import six

assets = (
    # '/images/favicon.ico',
    '/images/favicon.png',
    '/images/contrivers_icon_small.gif',
    '/css/screen.css',
    '/images/window_banner.png',
    '/images/contrivers_icon_large.jpg',
    '/js/responsive-nav.min.js',
    '/js/img.srcset.polyfill.js',
)

production_prefix = 'https://s3-us-west-1.amazonaws.com/contrivers-assets'
testing_prefix = '/static'

@pytest.mark.parametrize('path', assets)
def test_assets_with_testing(path, client):
    with client.get('/') as resp:
        expected = testing_prefix + path
        assert expected in resp.data

@pytest.mark.parametrize('path', assets)
def test_assets_with_production(path):
    from contrivers import create_app
    _app = create_app(
        'contrivers-unittests',
        testing=False,
        debug=False,
        additional_config_vars={
            'SQLALCHEMY_DATABASE_URI': "postgres://contrivers@localhost/contrivers-unittests",
            'SQLALCHEMY_ECHO': False,
            'WTF_CSRF_ENABLED': False,
            },
    )
    with _app.test_request_context():
        _app.extensions.get('sqlalchemy').db.drop_all()
        _app.extensions.get('sqlalchemy').db.create_all()
        with _app.test_client().get('/') as resp:
            expected = production_prefix + path
            assert expected in resp.data
