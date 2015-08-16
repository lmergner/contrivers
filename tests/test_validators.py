#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    tests.test_validators

    Test that when given a bunch of nearly correct isbn numbers, we get a
    consistent return from our model
"""
import unittest
from app.core.validators import validate_isbn
from app.core.errors import ValidationError


class TestISBN(unittest.TestCase):

    good_test_data = [
        (10, '0765378558', '0765378558'),
        (10, '076-53,78-558', '0765378558'),
        (13, '978-0765378552', '9780765378552'),
        (13, '978-076-537,8552', '9780765378552')
    ]

    bad_test_data = [
        (10, 'isbn0765378558'),  # has strings
        (13, '06978-0765378552'), # too long
        (13, '978378552'), # too short
    ]

    def test_validates(self):
        """ app.core.validators should handle well-formed isbns """
        for length, isbn, expected in self.good_test_data:
            self.assertEqual(validate_isbn(isbn, length), expected)

    def test_validate_fails(self):
        """ app.core.validators should raise an error on bad isbns """
        for length, isbn in self.bad_test_data:
            with self.assertRaises(ValidationError):
                validate_isbn(isbn, length)
