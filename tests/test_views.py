#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests.test_views
----------------

Tests for contrivers.www.views
"""
import pytest

#
# custom tests
#
def assert_status(resp, code):
    __tracebackhide__ = True
    if resp.status_code != code:
        pytest.fail('expected %s resp.status_code of 200' % resp.location)

def assert_200(resp):
    __tracebackhide__ = True
    assert_status(resp, 200)

def assert_redirects(resp, loc):
    __tracebackhide__ = True
    mes = "expected 301 or 302 for %s but got %d" % (loc, resp.status_code)
    if not resp.status_code in (301, 302) or \
            resp.location != "http://localhost" + loc:
        pytest.fail(mes)

def assert_template(template, client):
    __tracebackhide__ = True
    template_names = [t.name for t in client._test_templates]
    if template not in template_names:
        pytest.fail('expected %s to be in %s' % (template, client._test_templates))

def assert_context(ctx_var, client):
    __tracebackhide__ = True
    used = False
    for template in client._test_templates.keys():
        if ctx_var in client._test_templates[template]:
            used = True
    if not used:
        pytest.fail('expected to find %s in template context' % ctx_var)

def get_context(ctx_var, client):
    return client._test_templates.get(ctx_var, None)

def assert_content(resp, html):
    __tracebackhide__ = True
    if not html in resp.data:
        pytest.fail('Expected %s in resp.data' % html)

#
# Static / non-variable endpoints
#
def test_masthead(client):
    with client.get('/masthead/') as resp:
        assert_200(resp)
        assert_template('static.html', client)
        assert_content(resp, '<h1 id="mock-masthead">Mock Masthead</h1>')

def test_support(client):
    with client.get('/support/') as resp:
        assert_200(resp)
        assert_content(resp, 'Support')
        assert_template('support.html', client)

def test_sitemap(client):
    with client.get('/sitemap.xml') as resp:
        assert_200(resp)
        assert_template('sitemap.xml', client)

# TODO: favicon should be served from static files
def test_favicon(client):
    with client.get('/favicon.ico') as resp:
        assert_200(resp)
#
# Content endpoints
#
def test_index(client):
    with client.get('/') as resp:
        assert_200(resp)
        assert_template('index.html', client)

@pytest.mark.parametrize('url', [
    '/archive/',
    '/articles/',
    '/readings/',
    '/reviews/',
    '/articles/featured/',
])
def test_articles(client, url):
    with client.get(url) as resp:
        assert_200(resp)
        assert_template('articles.html', client)

def test_authors(client):
    with client.get('/authors/') as resp:
        assert_200(resp)
        assert_template('authors.html', client)

def test_categories(client):
    with client.get('/categories/') as resp:
        assert_200(resp)
        assert_template('tags.html', client)

def test_search(client):
    with client.get('/search/') as resp:
        assert_200(resp)
        assert_template('search.html', client)

def test_search_with_param(client):
    with client.post('/search/', data={'search_term': 'Habermas'}) as resp:
        assert_200(resp)
        assert_template('search.html', client)
        assert_context('search_term', client)
        assert get_context('search_term', client) == 'Habermas'

#
# Redirects
#
@pytest.mark.parametrize('url', [
    ('/subscribe/', '/support/'),
    ('/issues/', '/'),
    ('/article/', '/articles/'),
    ('/article/1/', '/articles/1/'),
    ('/catalog/', '/'),
    ('/catalog/?filter=reviews', '/reviews/'),
    ('/catalog/?filter=articles', '/articles/'),
    ('/featured/', '/articles/featured/')

])
def test_redirects(client, url):
    start, end = url
    with client.get(start) as resp:
        assert_redirects(resp, end)

@pytest.mark.parametrize('url', [
    '/',
    '/issues/',
    '/authors/',
    '/articles/'
])
def test_no_post_allowed(client, url):
    with client.post(url) as resp:
        assert_status(resp, 405)

@pytest.mark.parametrize('url', [
    '/posts/',
    '/all/',
    '/admin/',
    '/login',
    '/logout',
    '/cms/'
])
def test_removed(client, url):
    with client.get(url) as resp:
        assert_status(resp, 404)

def test_review_200(client, data):
    review = data.review()
    data.add_and_commit(review)
    with client.get('/reviews/{}/'.format(review.id)) as resp:
        assert_200(resp)
        assert_template('article.html', client)
        assert_content(resp, 'Test Review')
        assert_content(resp, 'Michel Foucault')

def test_article_200(client, data):
    article = data.article()
    data.add_and_commit(article)
    with client.get('/articles/{}/'.format(article.id)) as resp:
        assert_200(resp)
        assert_content(resp, 'Luke Thomas Mergner')
        assert_template('article.html', client)

def test_author_200(client, data):
    author = data.author()
    data.add_and_commit(author)
    with client.get('/authors/{}/'.format(author.id)) as resp:
        assert_200(resp)
        assert_template('author.html', client)

def test_tag_200(client, data):
    tags = data.tags()
    data.add_all_and_commit(tags)
    with client.get('/categories/1/') as resp:
        assert_200(resp)
        assert_template('tag.html', client)
