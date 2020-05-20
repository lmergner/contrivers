# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,missing-docstring,protected-access
"""
    tests.conftest
    --------------

    pytest fixtures
"""

import os
import random
import string
import codecs
import datetime
import warnings
from collections import Iterable
import pytest
from flask import templating, url_for
import jinja2
from sqlalchemy.engine.url import make_url
from contrivers import create_app
from contrivers.models import Article, Author, Tag, Book, Review


DATABASE_URL = make_url(os.environ.get("DATABASE_URL"))
DATABASE_URL.database += "-unitests-" + datetime.datetime.now().strftime("%m-%d-%H-%M-%S")

CONFIG_VARS = {
    'SQLALCHEMY_DATABASE_URI': DATABASE_URL,
    'SQLALCHEMY_ECHO': False,
    'WTF_CSRF_ENABLED': False,
}


def pytest_report_header(config):  # pylint: disable=unused-argument
    return "DB: {}".format(CONFIG_VARS['SQLALCHEMY_DATABASE_URI'])


def uopen(path):
    """ Open a file using the utf-8 codec """
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def test_config():
    return CONFIG_VARS


@pytest.fixture
def jinja_env(mocker):
    """ Return a mocked jinja environment with our custom globals and filters"""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('contrivers/templates'),
        extensions=['jinja2.ext.with_'])
    env.filters['md'] = lambda x: x
    env.globals['url_for'] = mocker.MagicMock(url_for)
    return env


@pytest.yield_fixture
def app(mocker, monkeypatch):
    """ yield a Flask app with a test_requst_context pushed """

    # Surpress the Flask-Cache set to null warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        _app = create_app(
            'contrivers-unittests',
            testing=True,
            debug=False,
            additional_config_vars=CONFIG_VARS
        )

    db = _app.extensions.get('sqlalchemy').db
    # mock out aws
    # but be careful because this returns a fake masthead
    # for every request and so if I need to test S3 later
    # this will break those tests
    mock_s3 = mocker.Mock(return_value="# Mock Masthead ")
    monkeypatch.setattr('contrivers.www.views.aopen', mock_s3)

    _ctx = _app.test_request_context()
    _ctx.push()
    db.drop_all()
    db.create_all()

    yield _app

    _ctx.pop()
    del _ctx
    del _app


@pytest.yield_fixture
def client(app):
    """ yield a flask test_client that keeps track of templates used"""
    client = app.test_client()
    client._test_templates = {}
    __original_renderer = templating._render
    def render_template_monkeypatch(template, ctx, app):
        client._test_templates[template] = ctx
        return __original_renderer(template, ctx, app)
    templating._render = render_template_monkeypatch
    yield client
    templating._render = __original_renderer


class Fixtures(object):
    """ Functions for building test data """

    def __init__(self, db):
        # cache the results so we can reliably retrieve them in a test
        self._tags = None
        self._authors = None
        self._articles = None
        self._reviews = None
        self._books = None
        self.db = db

    def add_and_commit(self, item):
        self.db.session.add(item)
        return self.db.session.commit()

    def add_all_and_commit(self, items):
        self.db.session.add_all(items)
        return self.db.session.commit()

    @staticmethod
    def random_date(end_days):
        sdate = datetime.datetime.utcnow()
        offset = random.randint(1, end_days)
        new_delta = datetime.timedelta(days=offset)
        return sdate + new_delta

    @staticmethod
    def path_to_data_files(filename):
        """ Return a path to the file name in the testing directory. Used for
        loading test assets like markdown text. """
        root = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(root, filename)

    @staticmethod
    def rand_isbn(length):
        return u''.join(
            random.choice(string.digits)
            for _ in range(length))

    def tags(self):
        if self._tags is None:
            self._tags = [
                Tag(tag='Political Theory'),
                Tag(tag='Essay'),
                Tag(tag='Polemics')
            ]
        return self._tags

    @staticmethod
    def author():
        return Author(
            name='Luke Thomas Mergner',
            email='lmergner@example.com',
            bio='This is an author biography.',
            twitter='lmergner',
            hidden=False
        )

    def authors(self, num):
        if self._authors is None:
            self._authors = []
            for idx in range(1, num + 1):
                self._authors.append(Author(
                    name=u'Author Name_{}'.format(idx),
                    email=u'author_{}@example.com'.format(idx),
                    bio=u'This is an author_{} biography'.format(idx),
                    twitter=u'author_{}'.format(idx),
                    hidden=False))
        return self._authors

    def article(self):
        return Article(
            title='Test Article',
            publish_date=datetime.datetime.utcnow(),
            text=uopen(self.path_to_data_files('markdown.md')),
            abstract='A test [markdown file](http://www.google.com) with a very short description',
            hidden=False,
            featured=False,
            authors=[self.author()],
            tags=[random.choice(self.tags())],
            responses=[])

    def articles(self, num, authors=None):
        if self._articles is None:
            self._articles = []
            if authors is None:
                authors = [self.author()]
            elif not isinstance(authors, Iterable):
                authors = [authors]
            else:
                pass
            for author in authors:
                for idx in range(1, num+1):
                    self._articles.append(Article(
                        title='Test Article {}'.format(idx),
                        publish_date=self.random_date(random.randint(1, 14)),
                        text=uopen(self.path_to_data_files('markdown.md')),
                        abstract=\
                            'A test [markdown file](http://www.google.com) ' + \
                            'with a very short description',
                        hidden=False,
                        featured=False,
                        authors=[author],
                        tags=[random.choice(self.tags())],
                        responses=[]))
        return self._articles

    def book(self, num=1):
        return Book(
            title='The History of Sexuality, Volume {}'.format(num),
            subtitle='An Introduction',
            author='Michel Foucault',
            publisher='Vintage Books',
            city='New York',
            year=1978,
            isbn_10=self.rand_isbn(10),
            isbn_13=self.rand_isbn(13),
            pages=100,
            price=1295
        )

    def books(self, num):
        if self._books is None:
            self._books = [self.book(num=idx) for idx in range(num)]
        return self._books

    def review(self):
        return Review(
            title='Test Review',
            publish_date=datetime.datetime.utcnow(),
            text=uopen(self.path_to_data_files('markdown.md')),
            abstract='A test [markdown file](http://www.google.com) with a very short description',
            hidden=False,
            featured=False,
            authors=[self.author()],
            tags=[random.choice(self.tags())],
            book_reviewed=[self.book()]
        )

    def reviews(self, num, authors=None):
        if self._reviews is None:
            self._reviews = []
            if authors is None:
                authors = [self.author()]
            elif not isinstance(authors, Iterable):
                authors = [authors]
            else:
                pass
            for author in authors:
                for idx in range(1, num+1):
                    self._reviews.append(Review(
                        title='Test Article {}'.format(idx),
                        publish_date=self.random_date(random.randint(1, 14)),
                        text=uopen(self.path_to_data_files('markdown.md')),
                        abstract=\
                            'A test [markdown file](http://www.google.com) ' + \
                            'with a very short description',
                        hidden=False,
                        featured=False,
                        authors=[author],
                        tags=[random.choice(self.tags())],
                        responses=[],
                        book_reviewed=[self.book(num=idx)]))
        return self._reviews


@pytest.fixture
def data(app): # pytest: disable=unused-argument
    """ a fixture that creates test data """
    return Fixtures(app.extensions.get('sqlalchemy').db)
