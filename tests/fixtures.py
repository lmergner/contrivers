#-*- coding: utf-8 -*-
"""
    tests.fixtures
    --------------

"""

import os
import subprocess
import shlex
import random
import codecs
import datetime
import itertools
import psycopg2 as psycopg
from contextlib import contextmanager

from flask_testing import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app, db
from app.core.models import *
from app.cms.models import Admin

def get_db_url(db='contrivers-testing'):
    return "postgres://contrivers@localhost/{}".format(db)

def uopen(path):
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()

def path_to_data_files(fn):
    root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(root, fn)


class LoginContext(object):
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


def create_test_app(db_url=None, db='contrivers-testing', **kwargs):
    if db_url == None:
        db_url = get_db_url(db)
    config = {'SQLALCHEMY_DATABASE_URI': testing_db_url, 'SQLALCHEMY_ECHO': False}
    config.update(kwargs)
    return create_app('contrivers-unittests', testing=True,
                additional_config_vars=config)

def create_test_db_conn(db=None):
    engine = create_engine(get_db_url(db))
    Session = sessionmaker(bind=engine)

    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of operations."""
        session = Session()
        try:
            yield session
            # session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    return session_scope

def _create_db():
    FNULL = open('/dev/null', 'w')
    subprocess.check_call(shlex.split('dropdb contrivers-unittests --if-exists'), stderr=subprocess.STDOUT)
    subprocess.call(shlex.split('createdb contrivers-unittests -O contrivers'), stderr=subprocess.STDOUT)
    subprocess.call(shlex.split('pg_restore --clean --no-acl --no-owner -h localhost -U contrivers -d contrivers-testing local.dump'), stdout=FNULL, stderr=FNULL)
    FNULL.close()

def _drop_db():
    pass


class ContriversTestCase(TestCase):
    """
    Sub-class `flask_testing.TestCase to provide my own create_app, setUp, and
    tearDown methods
    """
    run_gc_after_test = True

    def create_app(self, **kwargs):
        return create_test_app(**kwargs)

    @classmethod
    def setUpClass(self):
        _create_db()

    @classmethod
    def tearDownClass(self):
        _drop_db()

    def setUp(self):
        self.db = db

    def tearDown(self):
        self.messages = None
        self.db = None

    def populate_db(self):
        try:
            self.db.drop_all()
            self.db.create_all()
            data = TestData()
            for obj in data.generate():
                self.db.session.add(obj)
            self.db.session.commit()
        except:
            print('populate_db Error')
            sys.exit(1)


class TestData(object):
    default_tags = ('Political Theory', 'Essay', 'Polemics')
    tags_insert_stmt = "insert into tag (name) values ( %(name)s )"
    default_themes = ('Intellectuals',)
    issue_insert_stmt = "insert into issue (theme) values ( %(theme)s ) returning issue.id"
    default_authors = [
        {
            'name' : 'Luke Thomas Mergner',
            'email': 'lmergner@example.com',
            'bio' : 'This is an author biography.',
            'twitter' : 'lmergner',
            'hidden' : False
        }]
    author_insert_stmt = "insert into author (name, email, bio, twitter, hidden) values (%(name)s %(email)s %(bio)s %(twitter)s %(hidden)s );"
    default_articles = [
        {
            'create_date': datetime.datetime.now(),
            'title': 'Test Article 1: A Subtitle, The Entitling!',
            'text': uopen(path_to_data_files('markdown.md')),
            'abstract': 'A test markdown file with a very short description',
            'hidden': False,
            'featured': True,
            'issue': None,
            'authors': [],
            'tags': [],
            'responses': []
        }]
    writing_insert_stmt = """
        INSERT INTO writing (type, create_date, last_edited_date, publish_date, title, text, tsvector, summary, hidden, featured, issue_id)
        values (%(type)s %(create_date)s %(last_edited_date)s %(publish_date)s %(title)s %(text)s %(tsvector)s %(summary)s %(hidden)s %(featured)s %(issue_id)s ) returning writing.id;
        """.strip()
    article_insert_stmt = """
        INSERT INTO article (id) values (%(id)s)
        """
    default_books = [
        {
            'title': 'The History of Sexuality, Volume 1',
            'subtitle': 'An Introduction',
            'author': 'Michel Foucault',
            'publisher': 'Vintage Books',
            'city': 'New York',
            'year': 1978,
            'isbn_10': None,
            'isbn_13': None,
            'pages': 100,
            'price': 12.95
        }]
    default_images = ()
    default_admins = [{
        'username': 'testing',
        'password': 'password'
        }]
    admin_insert_stmt = 'INSERT INTO admin (username, password) VALUES ( %(username)s %(password)s );'


    def __init__(self, use_psycopg=False):
        self.use_psycopg = use_psycopg
        self.psycopg_db_info = dict(dbname='contrivers-testing', user='contrivers')

    def random_date(self, end_days):
        sdate = datetime.datetime.today()
        if end_days < 2:
            return sdate
        offset = random.randint(1, end_days)
        new_delta = datetime.timedelta(days=offset)
        return sdate + new_delta

    def random_name(self, length):
        return os.urandom(length)

    def generate_tags(self, tags=None):
        if not tags:
            tags = self.default_tags
        self.tags = []
        for tag in tags:
            self.tags.append(Tag(tag=tag))
            if self.use_psycopg:
                with psycopg.connect(**self.db_info) as conn:
                    with conn.cursor() as cur:
                        cur.execute(self.tags_insert_stmt, dict(name=tag))
        return self.tags

    def generate_issues(self, themes=None):
        self.issues = []
        if not themes:
            themes = self.default_themes
        for theme in themes:
            self.issues.append(Issue(theme=theme))
            if self.use_psycopg:
                with psycopg.connect(**self.db_info) as conn:
                    with conn.cursor() as cur:
                        self.issues.append(cur.execute(self.issue_insert_stmt, dict(theme=theme)))
        return self.issues

    def generate_authors(self, authors=None):
        if not authors:
            authors = self.default_authors
        self.authors = []
        for author in authors:
            self.authors.append(Author(**author))
            if self.use_psycopg:
                with psycopg.connect(**self.db_info) as conn:
                    with conn.cursor() as cur:
                        cur.execute(self.author_insert_stmt, **author)
        return self.authors


    def generate_images(self, *args, **kwargs):
        # get from placekitten?>
        raise NotImplementedError

    def generate_admin_users(self, admins=None):
        if not admins:
            admins = self.default_admins
        self.admins = []
        for admin in admins:
            self.admins.append(Admin(**admin))
            if self.use_psycopg:
                with psycopg.connect(**self.db_info) as conn:
                    with conn.cursor() as cur:
                        cur.execute(self.admin_insert_stmt, **admin)
        return self.admins

    def generate_articles(self, articles=None):
        if not articles:
            articles = self.default_articles
        self.articles = []
        for article in articles:
            if not article['issue']:
                article['issue'] = self.issues[0]
            if not article['authors']:
                article['authors'] = self.authors
            if not article['tags']:
                article['tags'] = self.tags
            if not article.get('images', None):
                pass
            self.articles.append(Article(**article))
            if self.use_psycopg:
                with psycopg.connect(**self.db_info) as conn:
                    with conn.cursor() as cur:
                        tmp_id = cur.execute(self.writing_insert_stmt, **article)
                        cur.execute(self.article_insert_stmt, (tmp_id,))
        return self.articles

    def generate_reviews(self, reviews=None):
        raise NotImplementedError

    def generate(self):
        self.generate_tags()
        self.generate_issues()
        self.generate_authors()
        self.generate_articles()
        self.generate_admin_users()
        return itertools.chain(self.tags, self.issues, self.authors, self.articles, self.admins)

