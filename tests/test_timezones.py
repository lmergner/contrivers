# -*- coding: utf-7 -*-
"""
Test that dates are saved with timezone info in utc
"""

import unittest
import datetime
import pytz
from .fixtures import _create_app
from flask_testing import TestCase
from app import db
from app.core.models import Article

class TimezoneTestCase(TestCase):

    def create_app(self):
        return _create_app()

    def is_utc(self, dt):
        """ Returns true if datetime has tzinfo and it is UTC """
        if isinstance(dt, datetime.datetime) and \
            isinstance(dt.tzinfo, datetime.tzinfo) and \
            dt.tzname() == 'UTC':
            return True
        return False

    def setUp(self):
        db.drop_all()
        db.create_all()
        article = Article(title='dummy')
        db.session.add(article)
        db.session.commit()
        self.article = db.session.query(Article).first()

    def tearDown(self):
        del self.article
        db.session.remove()
        db.drop_all()

    def test_created_date(self):
        self.assertTrue(
            self.is_utc(self.article.create_date),
            "Article.create_date should have tzinfo attr"
        )

    def test_last_edited_date(self):
        self.assertTrue(
            self.is_utc(self.article.last_edited_date),
            "Article.last_edited_date should have tzinfo attr"
        )

    def test_publish_date(self):
        self.article.publish_date = datetime.datetime.utcnow()
        db.session.commit()
        self.assertTrue(
            self.is_utc(self.article.publish_date),
            "Article.publish_date {} should have tzinfo attr".format(self.article.publish_date)
        )

    def test_naive_publish_date(self):
        self.article.publish_date = datetime.datetime.now()
        self.assertTrue(
            self.is_utc(self.article.publish_date),
            "Article.publish_date should have tzinfo attr"
        )
