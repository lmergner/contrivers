#-*- coding: utf-8 -*-
"""
    tests.fixtures
    --------------

"""

import os
import random
import codecs
import datetime
import warnings

from app import create_app
from app.core.models import Article, Author, Tag, Book, Review


def random_date(end_days):
    sdate = datetime.datetime.today()
    if end_days < 2:
        return sdate
    offset = random.randint(1, end_days)
    new_delta = datetime.timedelta(days=offset)
    return sdate + new_delta


def uopen(path):
    """ Open a file using the utf-8 codec """
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def load_env():
    """ Return the root .env file as a dict for loading into the app config """
    env = uopen('.env').strip()
    cfg = {}
    for line in env.split('\n'):
        k, v = line.split('=')
        cfg[k] = v
    return cfg


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


class AppMixin(object):
    """ Return a Flask app for flask-testing """

    def create_app(self):
        config_vars = {}
        config_vars.update(load_env())
        config_vars.update({
            'TESTING': True,
            'DEBUG': False,
            'SQLALCHEMY_DATABASE_URI': "postgresql://contrivers@localhost/contrivers-unittests",
            'SQLALCHEMY_ECHO': False,
        })
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')  # Surpress the Flask-Cache set to null warning
            app = create_app(
                'contrivers-unittests',
                testing=True,
                additional_config_vars=config_vars
            )
        return app


class Defaults(object):
    tags = [
        Tag(tag='Political Theory'),
        Tag(tag='Essay'),
        Tag(tag='Polemics')
    ]
    author = Author(
        name='Luke Thomas Mergner',
        email='lmergner@example.com',
        bio='This is an author biography.',
        twitter='lmergner',
        hidden=False
    )
    article = Article(
        title='Test Article',
        publish_date=datetime.datetime.utcnow(),
        text=uopen(path_to_data_files('markdown.md')),
        abstract='A test [markdown file](http://www.google.com) with a very short description',
        hidden=False,
        featured=False,
        authors=[author],
        tags=[random.choice(tags)],
        # 'responses'=[]
    )
    book = Book(
        title='The History of Sexuality, Volume 1',
        subtitle='An Introduction',
        author='Michel Foucault',
        publisher='Vintage Books',
        city='New York',
        year=1978,
        isbn_10='0679724699',
        isbn_13='978-0-679-72469-8',
        pages=100,
        price=1295
    )
    review = Review(
        title='Test Review',
        publish_date=datetime.datetime.utcnow(),
        text=uopen(path_to_data_files('markdown.md')),
        abstract='A test [markdown file](http://www.google.com) with a very short description',
        hidden=False,
        featured=False,
        authors=[author],
        tags=[random.choice(tags)],
        book_reviewed=[book]
    )
