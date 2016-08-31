# -*- coding: utf-8 -*-
"""
    tests/test_assets

    We don't care if the asset can be loaded (i.e. 200 or 404).
    Instead, we care if the template prints the expected url
    when the testing flag is set (local) or unset (s3).
"""

import pytest
from flask import url_for

assets = (
    'images/favicon.ico',
    'images/favicon.png',
    'images/contrivers_icon_small.gif',
    'css/screen.css',
    'images/window_banner.png',
    'images/contrivers_icon_large.jpg',
    'js/responsive-nav.min.js',
    'js/img.srcset.polyfill.js',
)

expected_TESTING_prefix = '/'
expected_PRODUCTIION_prefix = ''

@pytest.fixture
def mock_url_for(mocker):
    mocked = mocker.Mock(url_for)


@pytest.mark.parametrize('path', assets)
def test_assets_reachable(path, client):
    with client.get(path) as resp:
        assert path in resp.text

# TODO: favicon should be served from static files
def test_favicon(client):
    with client.get('/favicon.ico') as resp:
        assert_200(resp)
