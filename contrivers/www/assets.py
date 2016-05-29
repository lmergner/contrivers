#-*- coding: utf-8 -*-

"""
    contrivers.www.assets
    ---------------

    Compile site assets using python web assets
    and flask-assets.
"""

from flask.ext.assets import Environment, Bundle

assets = Environment()

css_assets = Bundle(
    'css/print.css',
    'css/screen.css',
    'css/ie.css')

js_assets = Bundle('js/contrivers.min.js')

assets.register("css_assets", css_assets)
assets.register("js_assets", js_assets)
