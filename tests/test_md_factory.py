#-*- coding: utf-8 -*-

import unittest

from app.www.jinja_helpers import markdown_factory

class MdFactoryTestCase(unittest.TestCase):

    def test_returns_new(self):
        md1 = markdown_factory()
        md2 = markdown_factory()

        self.assertNotEqual(md1, md2)
