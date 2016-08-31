# -*- coding: utf-7 -*-
"""
    tests.test_timezones

    all dates should be stored as utc tz-ignorant datetimes
"""

import pytest
import datetime
import psycopg2


@pytest.yield_fixture
def cursor(test_config):
    try:
        url = test_config.get('SQLALCHEMY_DATABASE_URI')
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        yield cur

    except TypeError as err:
        pytest.fail(err)

    except psycopg2.Error as err:
        pytest.fail(err)

    finally:
        cur.close()
        conn.close()
        del conn


def is_datetime(dt):
    if isinstance(dt, datetime.datetime):
        return
    pytest.fail('Expected a datetime object')


def is_utc(dt):
    """ Returns true if datetime has tzinfo and it is UTC """
    if dt.tzname() == 'UTC':
        return
    pytest.fail('Expected datetime to have UTC')


@pytest.mark.parametrize('attr', (
    'create_date',
    'last_edited_date',
    'publish_date',
))
def test_dates_are_utc(app, data, attr):
    """Article dates should be timezone aware and UTC """
    article = data.article()
    data.add_and_commit(article)

    dt = getattr(article, attr)
    is_datetime(dt)
    is_utc(dt)


def test_added_date(app, data, cursor):
    """ Test that dates in the database are naive. Bypass SQLAlchemy """
    article = data.article()
    data.add_and_commit(article)

    cursor.execute('SELECT create_date, last_edited_date, publish_date FROM writing LIMIT 1;')
    for row in cursor.fetchall():
        for dt in row:
            is_datetime(dt)
            assert dt.tzname() is None


def test_server_defaults(app, data, cursor):
    """ Test that the models are using server_defaults for dates """
    cursor.execute('INSERT INTO writing (title, type) VALUES (%s, %s);', ('test title', 'writing',))
    cursor.execute('SELECT create_date, last_edited_date FROM writing LIMIT 1;')
    for row in cursor.fetchall():
        for dt in row:
            is_datetime(dt)
            assert dt.tzname() is None
