# -*- coding: utf-8 -*-
import pytest

assets = (
    'images/favicon.ico',
    'images/favicon.png',
    'images/contrivers_icon_small.gif',
    'css/screen.css',
    'images/window_banner.png',
    'images/contrivers_icon_large.jpg',
    'js/responsive-nav.min.js',
    'js/img.srcset.polyfill.js',
    'masthead.md',
)

@pytest.mark.parametrize('path', assets)
def test_assets_reachable(path, client):
    with client.get(path) as resp:
        assert resp.status_code == 200
