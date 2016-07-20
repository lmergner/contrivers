# -*- coding: utf-8 -*-
"""
    tests.macros

    Tests for jinja macros
"""

import pytest
import jinja2
from flask.helpers import url_for


class MockPagination(object):
    """ Mock the behavior of Flask's paginated class """

    def __init__(self, items):
        self.items = items

class MockAuthor(object):
    """ Mock the attributes of the `app.models.Author` SQLAlchemy class """

    def __init__(self, *args, **kwargs):
        self.id = 1
        self.name = 'Dummy Author'
        self.email = 'dummy@example.com'
        self.twitter = 'dummy'
        self.bio = 'Dummy is a dummy who works at [dummy university](http://www.dummy_href.edu)'
        self.hidden = False
        self.url = lambda: '/author/1/dummy-author/'

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    @property
    def order(self):
        """ Raise an error if the app tries to use count to order_by """
        raise AttributeError('Author has no attribute order')

    @property
    def create_date(self):
        raise NotImplementedError

    @property
    def last_edited_date(self):
        raise NotImplementedError


def test_render_author_block(jinja_env):
    """jinja macro author block printing test

    Render the macro using a dummy template and dummy data. Then make
    assertions about how the macro formats data.
    """
    author = MockAuthor()
    mock_template = '\n'.join([
        "{% from 'macros.html' import render_author_block %}",
        "{{ render_author_block(author, show_articles=True, show_abstract=False, show_name=True ) | safe }}"
    ])
    template = jinja_env.from_string(mock_template)
    result = template.render(author=author)
    assert 'Dummy Author' in result
    assert "<a href='email://dummy@example.com'>dummy@example.com</a>" not in result

def test_render_authors(jinja_env):
    """ jinja macro author block should print without using author.count()

    Authors have no order_by or sort attribute, so they have to be
    sorted in the sqlalchemy search or by some other method. This was a
    bug. """

    authors = []

    for i in range(1, 6):
        authors.append(MockAuthor(id = i))

    mock_template = '\n'.join([
        "{% from 'macros.html' import render_authors %}",
        "{{ render_authors( paginated.items ) }}",
    ])
    template = jinja_env.from_string(mock_template)
    assert template.render(paginated=MockPagination(authors))  # Authors should not throw an error by calling author.order
