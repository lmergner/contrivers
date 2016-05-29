#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    tests.test_validators

    Test that when given a bunch of nearly correct isbn numbers, we get a
    consistent return from our model
"""
import pytest
from contrivers.core.validators import validate_isbn
from contrivers.core.errors import ValidationError


@pytest.mark.parametrize('success', [
    (10, u'0765378558', u'0765378558'),
    (10, u'076-53,78-558', u'0765378558'),
    (13, u'978-0765378552', u'9780765378552'),
    (13, u'978-076-537,8552', u'9780765378552')
])
def test_validates(success):
    """ app.core.validators should handle well-formed isbns """
    length, isbn, expected = success
    assert validate_isbn(isbn, length) == expected


@pytest.mark.parametrize('fails', [
    (10, 'isbn0765378558'),  # has strings
    (13, '06978-0765378552'), # too long
    (13, '978378552') # too short
])
def test_validate_fails(fails):
    """ app.core.validators should raise an error on bad isbns """
    length, isbn = fails
    with pytest.raises(ValidationError) as exc:
        validate_isbn(isbn, length)
