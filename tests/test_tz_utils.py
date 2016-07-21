"""
tests.test_tz_utils

tests for converting naive and aware datetimes to UTC
"""

import pytest
from datetime import datetime
from pytz import timezone
from contrivers.utils import has_timezone, with_utc


def test_has_timezone_naive():
    """ has_timezone should return False for naive datetimes """
    assert not has_timezone(datetime.utcnow())
    assert not has_timezone(datetime.now())

def test_has_timezone_aware():
    """ has_timezone should return True for aware datetimes """
    assert has_timezone(with_utc(datetime.utcnow()))

def test_with_utc_naive():
    """
    with_utc should return an aware datetime when given a naive datetime
    """
    assert with_utc(datetime.utcnow()).tzname() == 'UTC'

def test_with_utc_aware():
    """
    with_utc should convert an aware datetime from local to UTC
    """
    aware = timezone('US/Eastern').localize(datetime.utcnow())
    assert with_utc(datetime.utcnow()).tzname() == 'UTC'
