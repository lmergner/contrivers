# -*- coding: utf-8 -*-

import unittest
from app.www.jinja_helpers import md

class MDTestCase(unittest.TestCase):

    def test_headers(self):
        txt = "# Header One"
        expected = u"<h1>Header One</h1>"
        self.assertEqual(
            md(txt), expected,
            "app.www.jinja_helpers.md should handle headers")

