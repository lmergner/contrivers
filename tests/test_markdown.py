# -*- coding: utf-8 -*-

import pytest
from contrivers.www.jinja_helpers import markdown_factory

# TODO: write a full markdown test suite before switching to a different parser

def test_headers():
    """ Markdown -- test header renders as expected """
    txt = "# Header One"
    expected = u'<h1 id=\"header-one\">Header One</h1>'
    result = markdown_factory().convert(txt)
    assert result ==  expected

