# -*- coding: utf-8 -*-
"""
    test.test_rss

    Hit rss endpoints and validate the response against a DTD using lxml. This
    module can also be run from command line to debug problems
"""
import unittest
import mock
import argparse
import sys
import re
from StringIO import StringIO
from flask_testing import TestCase
from lxml import etree
from app import db, create_app
from app.core.models import Tag, Author
from app.www.rss import RssGenerator

# relative imports fail if called from command line
if __name__ != '__main__':
    from .fixtures import _create_app, Defaults

xml_endpoints = [
    '/rss/',
    '/articles/featured/rss/',
    '/articles/rss/',
    '/reviews/rss/',
    '/archive/rss/',
    ]
category_url_template = '/categories/{id}/rss/'
author_url_template = '/authors/{id}/rss/'

rss_dtd = """
    <!ELEMENT rss (channel)>
    <!ATTLIST rss version CDATA #IMPLIED>
    <!ATTLIST rss xmlns:content CDATA #IMPLIED>
    <!ATTLIST rss xmlns:atom CDATA #IMPLIED>

    <!ELEMENT channel (title+, link+, description+, copyright, docs, generator, language, lastBuildDate, item*)>
    <!ELEMENT item (title+, link+, description+, content:encoded, author+, guid, category?, pubDate)>
    <!ELEMENT title (#PCDATA)>
    <!ELEMENT link (#PCDATA)>
    <!ELEMENT description (#PCDATA)>
    <!ELEMENT copyright (#PCDATA)>
    <!ELEMENT docs (#PCDATA)>
    <!ELEMENT generator (#PCDATA)>
    <!ELEMENT language (#PCDATA)>
    <!ELEMENT lastBuildDate (#PCDATA)>
    <!ELEMENT author (#PCDATA)>
    <!ELEMENT guid (#PCDATA)>
    <!ATTLIST guid isPermaLink CDATA #IMPLIED>
    <!ELEMENT pubDate (#PCDATA)>
    <!ELEMENT content:encoded (#PCDATA)>
    <!ELEMENT category (#PCDATA)>
"""

def _validate_rss(rss):
    dtd = etree.DTD(StringIO(rss_dtd))
    xml = etree.XML(rss)
    return dtd.validate(xml)


class XmlEndpoints(TestCase):

    def create_app(self):
        return _create_app()

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def populate_db(self):
        """ Populate the db with test data

        articles = 2
        authors = 4
        tags = 3 randomly assigned
        featured = 1
        """
        defaults = Defaults()
        authors = defaults.authors(4)
        articles = reviews = []
        for x in range(4):
            if x % 2:
                articles.extend(defaults.articles(1, authors[x]))
            else:
                reviews.extend(defaults.reviews(1, authors[x]))
        articles[0].featured = True
        db.session.add_all(articles)
        db.session.add_all(reviews)
        db.session.commit()
        self.add_sub_urls_by_id(Tag.query.all(), category_url_template)
        self.add_sub_urls_by_id(Author.query.all(), author_url_template)

    def add_sub_urls_by_id(self, id_able, template):
        """ extend rss urls from a list of tags """
        xml_endpoints.extend([
            template.format(id=obj.id)
            for obj in id_able])

    def test_for_valid_xml(self):
        """ xml endpoints should return valid xml """
        self.populate_db()
        for xml in xml_endpoints:
            with self.client.get(xml) as resp:
                self.assertEqual(resp.status_code, 200, '{} returned {}'.format(xml, resp.status_code))
                self.assertTrue(_validate_rss(resp.data))
                # TODO: Ensure that RSS returns unicode data
                # self.assertIsInstance(resp.data, unicode)

    def test_no_emails(self):
        """ Test that no author emails are being publicized """
        self.populate_db()
        authors = Author.query.all()
        resp = self.client.get('/rss/')
        self.assert200(resp)
        for author in authors:
            self.assertNotIn(
                author.email,
                resp.data.decode('utf-8'),
                "email should not be in /authors/{}/rss/".format(author.id))


# TODO:  Test that the text is rendered through markdown
# @mock.patch('app.www.rss.markdown_factory')
# class TestGenerator(unittest.TestCase):

#     def test_rss_is_html(self, mocked):
#             resp = self.client.get('/rss/')
#             self.assert200(resp)
#             self.assertListEqual(mocked.mock_calls, [])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='RSS validator')
    parser.add_argument('--debug', action='store_true', help='Print debug info for DTD failures')
    parser.add_argument('db_url', default='contrivers', nargs='?')
    args = parser.parse_args()

    colors = {
        1: '\033[92mSUCCESS\033[0m',  # green
        2: '\033[93mWARN\033[0m',  # yellow
        3: '\033[91mFAIL\033[0m'  # red
        }

    def cprint(msg, level):
        if level not in range(1, 4):
            raise AttributeError("Print levels go from 1 to 3")
        print('{}: {}'.format(colors[level], msg))


    db_url = 'postgresql://contrivers@localhost/' + args.db_url

    app = create_app(
            __name__,
            testing=True,
            additional_config_vars={'SQLALCHEMY_DATABASE_URI': db_url, 'SQLALCHEMY_ECHO': False})

    def get_url(url):
        with app.test_request_context():
            c = app.test_client()
            if c.status_code != 200:
                cprint('{} returned a status of {}'.format(url, c.status_code), 3)
            return c.get(url)

    def test_rss(rss):
        try:
            dtd = etree.DTD(StringIO(rss_dtd))
            xml = etree.XML(resp.data)
            if dtd.validate(xml):
                cprint("{} validates".format(url), 1)
            else:
                cprint("{} does not validate".format(url), 2)
                if args.debug:
                    for err in dtd.error_log.filter_from_errors():
                        cprint(err, 3)
        except Exception as e:
            cprint(e, 3)
            if arg.debug:
                for idx, line in enumerate(rss_dtd.split('\n')):
                    try:
                        etree.DTD(StringIO(line))
                    except:
                        cprint("line {} failed".format(idx), 3)
            else:
                sys.exit(1)

    for url in xml_endpoints:
        resp = get_url(url)
        test_rss(resp.data)
