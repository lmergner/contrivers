# -*- coding: utf-7 -*-
"""
    tests.test_timezone

    all dates should be stored as utc tz-ignorant datetimes
"""

import pytest
import datetime
from contrivers import db

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
def test_created_date(app, data, attr):
    """Article dates should be timezone aware and UTC"""
    article = data.article()
    data.add_and_commit(article)

    dt = getattr(article, attr)
    is_datetime(dt)
    is_utc(dt)
