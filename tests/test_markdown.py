# -*- coding: utf-8 -*-

import unittest
from app.www.jinja_helpers import markdown_factory

class MDTestCase(unittest.TestCase):
    """ Asserts the behavior we expect so that we can later change markdown
    engines and catch changes """

    def md(self, txt):
        """ Run the markdown factory without registering
        the function as a jinja template"""
        return markdown_factory().convert(txt)

    def test_headers(self):
        """ Markdown -- test header renders as expected """
        txt = "# Header One"
        expected = u'<h1 id=\"header-one\">Header One</h1>'
        self.assertEqual(
            self.md(txt), expected,
            "app.www.jinja_helpers.markdown_factory should handle headers")

