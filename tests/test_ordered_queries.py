# -*- coding: utf-8 -*-

import unittest

from flask import request

from .fixtures import Defaults, _create_app
from flask_testing import TestCase
from contrivers.core.models import Author, Tag
from contrivers import db


class AuthorOrderTestCase(TestCase):
    """ from `app.views` queries should return a list of authors ordered by the
    sum or count of their `Author.writing` column """

    # flask-testing don't both with templates
    render_templates = False

    def create_app(self):
        return _create_app()

    def setUp(self):
        self.defaults = Defaults()
        self.authors = [x for x in self.defaults.authors(3)]
        articles = []
        articles.extend(self.defaults.articles(5, self.authors[0]))
        articles.extend(self.defaults.articles(3, self.authors[1]))
        articles.extend(self.defaults.articles(1, self.authors[2]))

        # Expect
        # author 1 has 5 articles
        # author 2 has 3 articles
        # author 3 has 1 article

        db.drop_all()
        db.create_all()
        db.session.add_all(articles)
        db.session.commit()

    def tearDown(self):
        del self.defaults
        del self.authors
        db.session.remove()
        db.drop_all()

    # @unittest.expectedFailure
    # def test_author_order(self):
    #     with self.client.get('/authors/') as resp:
    #         self.assertContext('authors', self.authors)
