# -*- coding: utf-8 -*-

import string
import unittest
import app.core.validators as validators
from app.core.errors import ValidationError
from app.core.models import Book


class ValidatorsTestCase(unittest.TestCase):

    data = {
        10: {
                'data': '0765378558',
                'expected': '0765378558'
            },
        13: {
                'data': '978-0765378552',
                'expected': '9780765378552'
            }
        }

    def test_filter_punctuation_10(self):
        """ Filtered 10 digit isbn should be identical"""
        result = validators.filter_punctuation(self.data[10]['data'])
        self.assertEqual(result, self.data[10]['expected'])

    def test_filter_punctuation_13(self):
        """ Filtered 13 digit isbn should strip hyphens """
        result = validators.filter_punctuation(self.data[13]['data'])
        self.assertEqual(result, self.data[13]['expected'])

    def test_is_numeric(self):
        for x in range(9):
            self.assertTrue(validators.is_numeric(str(x)), "is_numeric should return True for all single digits")

        for char in string.ascii_letters:
            self.assertFalse(validators.is_numeric(char))

    def test_validate_isbn_raises_on_alpha(self):
        """ validate_isbn should raise an error if the isbn contains non-digit characters """
        with self.assertRaises(ValidationError):
            validators.validate_isbn('string7890', 10)

    def test_validate_isbn_raises_on_too_long(self):
        """validate_isbn should raise an error on a too-long numeric string"""
        with self.assertRaises(ValidationError):
            validators.validate_isbn('12345678901', 10)

    def test_validate_isbn_returns(self):
        self.assertEqual(
            validators.validate_isbn(self.data[10]['data'], 10),
            self.data[10]['expected']
        )
        self.assertEqual(
            validators.validate_isbn(self.data[13]['data'], 13),
            self.data[13]['expected']
        )


class IsbnTestCase(unittest.TestCase):

    def setUp(self):
        self.book = Book()

    def tearDown(self):
        del self.book

    def test_isbn_10_length_constraint(self):
        with self.assertRaises(ValidationError):
            self.book.isbn_10 = '12345'

    def test_isbn_13_length_constraint(self):
        with self.assertRaises(ValidationError):
            self.book.isbn_13 = '0123456789'

    def test_isbn_10(self):
        self.book.isbn_10 = '0765378558'
        self.assertEqual(self.book.isbn_10, '0765378558')

    def test_isbn_13(self):
        self.book.isbn_13 = '978-0765378552'
        self.assertEqual(self.book.isbn_13, '9780765378552')
