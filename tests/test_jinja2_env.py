#-*- coding: utf-8 -*-

import unittest

from .fixtures import AppMixin

class JinjaTestCase(AppMixin, unittest.TestCase):

    def setUp(self):
        self.env = self.create_app().jinja_env

    def tearDown(self):
        del self.env

    def test_env_has_md_filter(self):
        self.assertIn('md', self.env.filters, "the jinja env should have a function called `md`")

