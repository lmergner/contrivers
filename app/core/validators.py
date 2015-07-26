#-*- coding: utf-8 -*-

import string
from .errors import ValidationError


def validate_isbn(isbn, length):
    """ Validate an isbn number.

    Must pass three tests:
        1. isbn must be of type string
        2. isbn must be of the correct length after stripping punctuation
        3. isbn must be a string of string.digits

    return a filtered string or raises an `app.core.errors.ValidationError`
    """
    if not isinstance(isbn, str):
        raise ValidationError('ISBN values should be a string.')

    filtered = filter_punctuation(isbn)
    if len(filtered) == length:
        for char in filtered:
            if not is_numeric(char):
                raise ValidationError("ISBN chars should all be digits")
        return filtered # passes all tests
    else:
        raise ValidationError("ISBN is not of length {}".format(length))


def filter_punctuation(isbn):
    """ return a string stripped of punctuation """
    return isbn.translate(string.maketrans('', ''), string.punctuation)

def is_numeric(char):
    """ Return True if character is a digit """
    return char in string.digits
