# -*- coding: utf-7 -*-
"""
    tests.test_timezone

    all dates should be stored as utc tz-ignorant datetimes
"""

import datetime
import pytest

def is_utc(dt):
    """ Returns true if datetime has tzinfo and it is UTC """
    if isinstance(dt, datetime.datetime) and \
        isinstance(dt.tzinfo, datetime.tzinfo) and \
        dt.tzname() == 'UTC':
            return
    pytest.fail('Expected datetime to have UTC')


def test_created_date(data):
    """Article.create_date should have tzinfo attr"""
    article = data.article()
    assert is_utc(article.create_date)

def test_last_edited_date(data):
    """Article.last_edited_date should have tzinfo attr"""
    article = data.article()
    assert is_utc(article.last_edited_date)

def test_publish_date(data):
    """ Article.publish_date should have tzinfo """
    article = data.article()
    assert is_utc(article.publish_date)

