# -*- coding: utf-8 -*-
"""
    tests.test_mem_cache

    Tests for a simple memoization function
"""

import pytest
from contrivers.utils import cache

class Identity(object):
    """ a mock function that keeps track of
    how many times it has been called
    """
    called = 0
    @cache
    def __call__(self, thing):
        self.called = self.called + 1
        return thing

identity = Identity()

def test_cache(mocker):
    expected_key = 'identity::blarg'
    expected_value = 'blarg'
    assert identity('blarg') == 'blarg'
    assert identity.called == 1
    assert identity('blarg') == 'blarg'
    assert identity.called == 1

    # TODO: refactor cache to expose the actual cache dictionary
    # assert cache  == {expected_key: expected_value}
