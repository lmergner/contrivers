# -*- coding: utf-8 -*-
"""
    tests.macros

    Tests for jinja macros
"""

import unittest
import jinja2
import mock
from flask.helpers import url_for


class MockPagination(object):
    """ Mock the behavior of Flask's paginated class """

    def __init__(self, items):
        self.items = items

class MockAuthor(object):
    """ Mock the attributes of the `app.core.models.Author` SQLAlchemy class """

    def __init__(self, *args, **kwargs):
        self.id = 1
        self.name = 'Dummy Author'
        self.email = 'dummy@example.com'
        self.twitter = 'dummy'
        self.bio = 'Dummy is a dummy who works at [dummy university](http://www.dummy_href.edu)'
        self.hidden = False

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    @property
    def order(self):
        raise AttributeError('Author has no attribute order')

    @property
    def create_date(self):
        raise NotImplementedError

    @property
    def last_edited_date(self):
        raise NotImplementedError


class MacrosTestCase(unittest.TestCase):

    def setUp(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('app/templates'), extensions=['jinja2.ext.with_'])
        self.env.filters['md'] = lambda x: x
        self.env.globals['url_for'] = mock.MagicMock(url_for)

    def tearDown(self):
        del self.env


class AuthorMacrosTestCase(MacrosTestCase):
    """ A regression test to make sure that the macro does not try to order
    a list of authors by author.order.  Ordering should be done in the query
    itself. """

    def test_render_author_block(self):
        author = MockAuthor()
        mock_template = '\n'.join([
            "{% from 'macros.html' import render_author_block %}",
            "{{ render_author_block(author, show_articles=True, show_abstract=False, show_name=True ) | safe }}"
        ])
        template = self.env.from_string(mock_template)
        result = template.render(author=author)
        self.assertIn('Dummy Author', result)
        self.assertNotIn("<a href='email://dummy@example.com'>dummy@example.com</a>", result)

    def test_render_authors(self):
        """ Authors have no order_by or sort attribute, so they have to be
        sorted in the sqlalchemy search or by some other method. This was a
        bug. """

        authors = []

        for i in range(1, 6):
            authors.append(MockAuthor(id = i))

        mock_template = '\n'.join([
            "{% from 'macros.html' import render_authors %}",
            "{{ render_authors( paginated.items ) }}",
        ])
        template = self.env.from_string(mock_template)
        assert template.render(paginated=MockPagination(authors))  # Authors should not throw an error by calling author.order
