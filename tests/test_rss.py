# -*- coding: utf-8 -*-
"""
    test.test_rss

    Hit rss endpoints and validate the response against a DTD using lxml. This
    module can also be run from command line to debug problems
"""

import pytest
import re
from io import StringIO
from lxml import etree
from contrivers import db, create_app
from contrivers.models import Tag, Author
from contrivers.www.rss import RssGenerator

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

def validate_rss(rss):
    """ validate the generated rss feeds using a DTD """
    dtd = etree.DTD(StringIO(rss_dtd))
    xml = etree.XML(rss)
    if not dtd.validate(xml):
        pytest.fail('RSS didn\'t validate')

@pytest.fixture
def populate(data):
    """ Populate the db with test data

    articles = 2
    authors = 4
    tags = 3 randomly assigned
    featured = 1
    """
    authors = data.authors(4)
    articles = reviews = []
    for x in range(4):
        if x % 2:
            articles.extend(data.articles(1, authors[x]))
        else:
            reviews.extend(data.reviews(1, authors[x]))
    articles[0].featured = True
    data.add_all_and_commit(articles)
    data.add_all_and_commit(reviews)

    add_sub_urls_by_id(Tag.query.all(), category_url_template)
    add_sub_urls_by_id(Author.query.all(), author_url_template)

def add_sub_urls_by_id(id_able, template):
    """ extend rss urls from a list of tags """
    xml_endpoints.extend([ template.format(id=obj.id)
        for obj in id_able])

def test_for_valid_xml(client, populate):
    """ xml endpoints should return valid xml """
    for xml in xml_endpoints:
        with client.get(xml) as resp:
            assert resp.status_code == 200
            validate_rss(resp.data)
            # TODO: Ensure that RSS returns unicode data
            # self.assertIsInstance(resp.data, unicode)

def test_no_emails(client, populate):
    """ Test that no author emails are being publicized """
    authors = Author.query.all()
    with client.get('/rss/') as resp:
        assert resp.status_code == 200
        for author in authors:
            assert author.email not in resp.data.decode('utf-8')


# TODO:  Test that the text is rendered through markdown
# @mock.patch('app.www.rss.markdown_factory')
# class TestGenerator(unittest.TestCase):

#     def test_rss_is_html(mocked):
#             resp = client.get('/rss/')
#             assert200(resp)
#             assertListEqual(mocked.mock_calls, [])

if __name__ == '__main__':
    import argparse
    import sys
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
