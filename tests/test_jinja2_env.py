#-*- coding: utf-8 -*-

import pytest

def test_env_has_md_filter(app):
    """the jinja env should have a function called `md`"""
    env = app.jinja_env
    assert 'md' in env.filters
