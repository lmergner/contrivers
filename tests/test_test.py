# -*- coding: utf-8 -*-
# pytest: disable=unused-import
"""
Sanity checking for pytest unittests

When migrating to pytest there was a problem with flask_sqlalchemy's
create_db() function. These tests run some basic assertions about the
testing environment.
"""

import pytest
from contrivers.models import *
from contrivers import db

@pytest.fixture
def tables(app):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
    result = db.engine.execute(query)
    tables = []
    for res in result:
        # query results are tuples, so unpack them
        tables.append(res[0])
    return tables

def test_db_url(app):
    assert app.config.get('SQLALCHEMY_DATABASE_URI').endswith('unittests')

def test_schema_was_created(tables):
    assert u'article' in tables
    assert u'writing' in tables

@pytest.mark.parametrize('table', db.metadata.tables)
def test_tables_are_empty(app, table):
    result = db.session.query(db.metadata.tables.get(table)).count()
    assert result == 0

def test_why_no_tables_exist(client):
    author = Author(
        name='blarg',
        email='blarg@example.com')
    article = Article(
        title='the blargest',
        authors=[author])

    db.session.add(article)
    db.session.commit()
