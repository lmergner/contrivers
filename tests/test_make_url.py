# -*- coding: utf-8 -*-

import unittest
from flask.ext.testing import TestCase
from .fixtures import _create_app, Defaults
from contrivers import db
from contrivers.core.models import Article, Author, Review

class MakeUrlTestCase(TestCase):

    def create_app(self):
        return _create_app()

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.defaults = Defaults()

    def tearDown(self):
        del self.defaults
        db.session.remove()
        db.drop_all()

    def test_article_url(self):
        article = self.defaults.article()
        self.assertEqual(article.url(), 'http://localhost/articles/')
        article.slug = '-'.join(article.title.lower().split())
        db.session.add(article)
        db.session.commit()
        article = Article.query.first()
        self.assertEqual(article.url(), 'http://localhost/articles/1/test-article/')


    def test_review_url(self):
        review = self.defaults.review()
        self.assertEqual(review.url(), 'http://localhost/reviews/')
        review.slug = '-'.join(review.title.lower().split())
        db.session.add(review)
        db.session.commit()
        review = Review.query.first()
        self.assertEqual(review.url(), 'http://localhost/reviews/1/test-review/')

    def test_author_url(self):
        author = self.defaults.author()
        self.assertEqual(author.url(), 'http://localhost/authors/')
        db.session.add(author)
        db.session.commit()
        author = Author.query.first()
        self.assertEqual(author.url(), 'http://localhost/authors/1/luke-thomas-mergner/')
