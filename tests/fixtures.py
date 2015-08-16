#-*- coding: utf-8 -*-
"""
    tests.fixtures
    --------------

"""

import os
import random
import string
import codecs
import datetime
import warnings
import mock
from collections import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.core.models import Article, Author, Tag, Book, Review


def random_date(end_days):
    sdate = datetime.datetime.utcnow()
    offset = random.randint(1, end_days)
    new_delta = datetime.timedelta(days=offset)
    return sdate + new_delta


def uopen(path):
    """ Open a file using the utf-8 codec """
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def path_to_data_files(filename):
    """ Return a path to the file name in the testing directory. Used for
    loading test assets like markdown text. """
    root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(root, filename)


class LoginContext(object):  # pylint: disable=too-few-public-methods
    """ context manager for login during testing. """

    def __init__(self, client, username='testing', password='password'):
        self.client = client
        self.username = username
        self.password = password

    def __enter__(self):
        resp = self.client.post('/login', data=dict(
            username=self.username,
            password=self.password
            ), follow_redirects=True)
        if resp.status_code != 200:
            raise Exception("login failed with code {}".format(
                resp.status_code))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.get('/logout', follow_redirects=True)

def _create_app(extra_vars={}):
    config_vars = {
        'TESTING': True,
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': "postgresql://contrivers@localhost/contrivers-unittests",
        'SQLALCHEMY_ECHO': False,
    }
    config_vars.update(extra_vars)
    # Surpress the Flask-Cache set to null warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        app = create_app(
            'contrivers-unittests',
            testing=True,
            additional_config_vars=config_vars
        )
    return app


class test_session(object):
    """ context manager that replaces the flask-sqalchemy interface for testing """

    engine = create_engine("postgresql://contrivers@localhost/contrivers-unittests")

    def __init__(self, *args, **kwargs):
        self.session = sessionmaker(bind=self.engine)

    def __enter__(self):
        try:
            return self.session
        except:
            self.session.rollback()

    def __exit__(self, error, value, traceback):
        self.session.remove()


class Defaults(object):

    def __init__(self):
        # cache the results so we can reliably retrieve the in a test
        self._tags = None
        self._authors = None
        self._articles = None
        self._reviews = None
        self._books = None

    def rand_isbn(self, length):
        return ''.join(
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

    def author(self):
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
            for x in range(1, num + 1):
                self._authors.append(Author(
                    name=u'Author Name_{}'.format(x),
                    email=u'author_{}@example.com'.format(x),
                    bio=u'This is an author_{} biography'.format(x),
                    twitter=u'author_{}'.format(x),
                    hidden=False))
        return self._authors

    def article(self):
        return Article(
            title='Test Article',
            publish_date=datetime.datetime.utcnow(),
            text=uopen(path_to_data_files('markdown.md')),
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
                for x in range(1, num+1):
                    self._articles.append(Article(
                        title='Test Article {}'.format(x),
                        publish_date=random_date(random.randint(1, 14)),
                        text=uopen(path_to_data_files('markdown.md')),
                        abstract='A test [markdown file](http://www.google.com) with a very short description',
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
            self._books = [self.book(num=x) for x in range(x, x+1)]
        return self._books

    def review(self):
        return Review(
            title='Test Review',
            publish_date=datetime.datetime.utcnow(),
            text=uopen(path_to_data_files('markdown.md')),
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
                for x in range(1, num+1):
                    self._reviews.append(Review(
                        title='Test Article {}'.format(x),
                        publish_date=random_date(random.randint(1, 14)),
                        text=uopen(path_to_data_files('markdown.md')),
                        abstract='A test [markdown file](http://www.google.com) with a very short description',
                        hidden=False,
                        featured=False,
                        authors=[author],
                        tags=[random.choice(self.tags())],
                        responses=[],
                        book_reviewed=[self.book(num=x)]))
        return self._reviews
