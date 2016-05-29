#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    tests.test_views
    ----------------

    Tests for contrivers.www.views
"""

import unittest
from flask_testing import TestCase
from .fixtures import Defaults, _create_app
from contrivers import db
from mock import patch

class UrlTestCase(TestCase):
    """Verify that the main urls exposed to the public work and
    have data that we expect."""

    def create_app(self):
        return _create_app()

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.defaults = Defaults()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del self.defaults

    #
    # Static / non-variable endpoints
    #
    def test_masthead(self):
        with patch('contrivers.www.views.aopen') as mock_boto:
            mock_boto.return_value = "# Mock Masthead "
            with self.client.get('/masthead/') as resp:
                self.assert200(resp)
                self.assertIn('<h1 id="mock-masthead">Mock Masthead</h1>', resp.data)

    def test_support(self):
        with self.client.get('/support/') as resp:
            self.assert200(resp)
            self.assertIn('Support', resp.data)
            self.assert_template_used('support.html')

    #
    # Content endpoints
    #
    def test_articles(self):
        with self.client.get('/articles/') as resp:
            self.assert200(resp)
            self.assertTemplateUsed('articles.html')

    def test_reviews(self):
        with self.client.get('/reviews/') as resp:
            self.assert200(resp)
            self.assertTemplateUsed('articles.html')

    def test_authors(self):
        with self.client.get('/authors/') as resp:
            self.assert200(resp)
            self.assertTemplateUsed('authors.html')

    def test_categories(self):
        from contrivers.core.models import Tag
        tags = sorted(db.session.query(Tag).all(), key=lambda x: x.count, reverse=True)
        with self.client.get('/categories/') as resp:
            self.assert200(resp)
            self.assertTemplateUsed('tags.html')
            self.assertEqual(self.get_context_variable('paginated').items, tags)

    def test_search_splash(self):
        self.assert200(self.client.get('/search/'))

    #
    # Redirects
    #
    def test_subscribe(self):
        self.assertStatus(self.client.get('/subscribe/'), 302)

    def test_issues(self):
        with self.client.get('/issues/') as resp:
            self.assertRedirects(resp, '/')

    def test_article(self):
        self.assertRedirects(self.client.get('/article/'), '/articles/')
        self.assertRedirects(self.client.get('/article/1/'), '/articles/1/')

    def test_catalog(self):
        self.assertRedirects(self.client.get('/catalog/'), '/')

    #
    # Authenticated access
    #
    def test_no_post_allowed(self):
        self.assertStatus(self.client.post('/issues/'), 405)
        self.assertStatus(self.client.post('/'), 405)
        self.assertStatus(self.client.post('/authors/'), 405)
        self.assertStatus(self.client.post('/articles/'), 405)

    def test_removed(self):
        self.assertStatus(self.client.post('/posts/'), 404)

    def test_old_archive_endpoint(self):
        self.assert404(self.client.get('/all/'))

    def test_review_200(self):
        review = self.defaults.review()
        db.session.add(review)
        db.session.commit()
        with self.client.get('/reviews/1/') as resp:
            self.assert200(resp)
            self.assertTemplateUsed('article.html')
            self.assertIn('Test Review', resp.data)
            self.assertIn('Michel Foucault', resp.data)

    def test_article_200(self):
        article = self.defaults.article()
        db.session.add(article)
        db.session.commit()
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(len(article.authors), 1)
        self.assertEqual(article.authors[0].name, "Luke Thomas Mergner")
        with self.client.get('/articles/{}/'.format(article.id)) as resp:
            self.assert200(resp)
            self.assertIn('Luke Thomas Mergner', resp.data)
            self.assertTemplateUsed('article.html')


