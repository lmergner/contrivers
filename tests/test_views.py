#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.test_views
    ----------------

    Tests for app.www.views
"""

import unittest
from .fixtures import ContriversTestCase


class URLTestCase(ContriversTestCase):
    """Verify that the main urls exposed to the public work and
    have data that we expect."""

    # Static / non-variable endpoints
    def test_index(self):
        # index
        self.assert200(self.client.get('/'))

    def test_masthead(self):
        # masthead
        self.assert200(self.client.get('/masthead/'))

    def test_support(self):
        self.assert200(self.client.get('/support/'))
    #
    # Content endpoints
    #
    def test_issues(self):
        self.assert200(self.client.get('/issues/'))

    def test_articles(self):
        self.assert200(self.client.get('/articles/'))

    def test_authors(self):
        self.assert200(self.client.get('/authors/'))

    def test_categories(self):
        self.assert200(self.client.get('/categories/'))

    def test_reviews(self):
        self.assert200(self.client.get('/reviews/'))

    def test_search_splash(self):
        self.assert200(self.client.get('/search/'))

    #
    # Redirects
    #
    def test_subscribe(self):
        self.assertStatus(self.client.get('/subscribe/'), 302)

    def test_article(self):
        self.assertStatus(self.client.get('/article/'), 302)
        self.assertStatus(self.client.get('/article/1/'), 302)

    def test_catalog(self):
        self.assertStatus(self.client.get('/catalog/'), 302)

    def test_no_post_allowed(self):
        self.assertStatus(self.client.post('/issues/'), 405)
        self.assertStatus(self.client.post('/'), 405)
        self.assertStatus(self.client.post('/authors/'), 405)
        self.assertStatus(self.client.post('/articles/'), 405)
        self.assertStatus(self.client.post('/issues/'), 405)

    def test_removed(self):
        self.assertStatus(self.client.post('/posts/'), 404)

    def test_archive(self):
        self.assert404(self.client.get('/all/'))


if __name__ == '__main__':
    unittest.main()
