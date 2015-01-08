#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.www.views
    ----------------

"""
from datetime import datetime, timedelta
from collections import namedtuple

from flask import (
    render_template, request, url_for, redirect, make_response, abort,
    current_app
)
from sqlalchemy import desc

from .forms import SearchForm
from .utils import aopen
from .rss import RssGenerator

from . import www
from .queries import page_query, id_query, index_query, _poly, search_query, paginate
from ..core import *


@www.context_processor
def set_site_info():
    return dict(search=SearchForm())

# @cache.cached(timeout=50)
@www.route('/')
def index():
    """ return the index page """
    featured, curr_issue = index_query()  # from app.www.queries
    return render_template(
        'index.html',
        featured=featured,
        current_issue=curr_issue,
        rss_url = url_for('.rss_index', _external=True))

@www.route('/rss/')
def rss_index():
    query = db.session.query(_poly).order_by('publish_date').limit(20)
    rss = RssGenerator(url_for('.index'), query)
    return make_response(rss.rss_str())

@www.route('/articles/featured/<int:page>/')
@www.route('/articles/featured/', defaults={'page': 1})
def featured(page):
    query = db.session.query(_poly).filter_by(featured=True)
    featureds = page_query(None, page, query=query)
    return render_template(
        'articles.html',
        paginated = featureds,
        endpoint='.featured',
        sort_by='publish_date',
        page_type='archive',
        rss_url = url_for('.rss_featured', _external=True))

@www.route('/articles/featured/rss/')
def rss_featured():
    query = db.session.query(_poly).filter_by(featured=True).order_by(_poly.publish_date.desc()).limit(20)
    rss = RssGenerator(url_for('.featured', _external=True), query, title=u"Contrivers' Review Featured")
    return make_response(rss.rss_str())

@www.route('/article/<int:id>')
@www.route('/article/', defaults={'id': None})
def redirect_article(id):
    return redirect(url_for('.articles', article_id=id))

@www.route('/articles/', defaults={'article_id': None, 'page': 1})
@www.route('/articles/<int:article_id>/', defaults={'page': 1})
@www.route('/articles/p/<int:page>/', defaults={'article_id': None})
def articles(article_id, page):
    if article_id is not None:
        rs = id_query(Article, article_id)
        return render_template('article.html', article=rs)
    else:
        rs = page_query(Article, page)
        return render_template(
            'articles.html',
            paginated=rs,
            endpoint='.articles',
            page_type='archive',
            rss_url = url_for('.rss_articles', _external=True))

@www.route('/articles/rss/')
def rss_articles():
    query = db.session.query(Article).order_by('publish_date').limit(20)
    rss = RssGenerator(url_for('.articles', _external=True), query, title=u"Contrivers’ Review Articles")
    return make_response(rss.rss_str())

@www.route('/reviews/', defaults={'review_id': None, 'page': 1})
@www.route('/reviews/<int:review_id>/', defaults={'page': 1})
@www.route('/reviews/p/<int:page>/', defaults={'review_id': None})
def reviews(review_id, page):
    # If we have an id, return one Writing and
    # send it to the review / reading template
    if review_id is not None:
        return render_template(
            'article.html',
            article = id_query(Review, review_id))
    else:
        return render_template('articles.html',
            paginated=page_query(Review, page),
            endpoint='.reviews',
            sort_by='publish_date',
            page_type='archive',
            rss_url = url_for('.rss_reviews', _external=True))

@www.route('/archive/', defaults={'page': 1})
@www.route('/archive/p/<int:page>/')
def archive(page):
        return render_template('articles.html',
            paginated=page_query(_poly, page),
            endpoint='.archive',
            sort_by='publish_date',
            page_type='archive',
            rss_url = url_for('.rss_reviews', _external=True))

@www.route('/archive/rss/')
def rss_archive():
    query = db.session.query(_poly).order_by('publish_date').limit(10)
    rss = RssGenerator(url_for('.archive', _external=True), query, title=u"Contrivers' Review Recent")
    return make_response(rss.rss_str())

@www.route('/reviews/rss/')
def rss_reviews():
    query = db.session.query(Review).order_by(Issue.issue_num.desc()).limit(10)
    rss = RssGenerator(url_for('.reviews'), query, title=u"Contrivers' Review Issues")
    return make_response(rss.rss_str())

@www.route('/issues/', defaults={'issue_id': None, 'page': 1})
@www.route('/issues/p/<int:page>/', defaults={'issue_id': None})
@www.route('/issues/<int:issue_id>/', defaults={'page': 1})
def issues(issue_id, page=1):
    if issue_id:
        return render_template(
            'issue.html',
            issue=id_query(Issue, issue_id))
    else:
        return render_template(
            'issues.html',
            paginated=page_query(Issue, page))

# @www.route('/issues/rss/')
# def rss_issues():
#     query = db.session.query(Issue).order_by('issue_num').limit(20)
#     rss = RssGenerator(url_for('.issues'), query, title=u"Contrivers' Review Book Reviews")
#     return make_response(rss.rss_str())

@www.route('/authors/', defaults={'author_id': None, 'page': 1})
@www.route('/authors/p/<int:page>/', defaults={'author_id': None})
@www.route('/authors/<int:author_id>/', defaults={'page': 1})
def authors(author_id, page):
    if author_id is not None:
        author = id_query(Author, author_id)
        return render_template(
            'author.html',
            page_type='authors',
            author=author,
            rss_url=url_for('.rss_author', author_id=author.id, _external=True))
    else:
        query =  db.session.query(Author).filter_by(hidden=False).filter(Author.writing.any())
        pages = paginate(query, page)
        return render_template(
            'authors.html',
            paginated = pages,
            endpoint='.authors',
            page_type='authors',
            sort_by='name')


@www.route('/authors/<int:author_id>/rss/')
def rss_author(author_id):
    author = id_query(Author, author_id)
    rss = RssGenerator(url_for('.authors', author_id=author.id), author.writing, title=u"{} Articles from Contriver' Review".format(author.name))
    return make_response(rss.rss_str())


@www.route('/categories/', defaults={'tag_id': None, 'page': 1})
@www.route('/categories/p/<int:page>/', defaults={'tag_id': None})
@www.route('/categories/<int:tag_id>/', defaults={'page': 1})
def tags(tag_id, page):
    if tag_id is not None:
        tag = db.session.query(Tag).get(tag_id)
        # TODO: Make a paginated query for tag.writings
        return render_template(
            'tag.html',
            tag=tag,
            page_type='tags',
            rss_url=url_for('.rss_tag', tag_id=tag.id, _external=True))
    else:
        results = page_query(None, page, db.session.query(Tag).filter(Tag.writing.any()))
        return render_template(
            'tags.html',
            paginated=results)


@www.route('/categories/<int:tag_id>/rss/')
def rss_tag(tag_id):
    tag = id_query(Tag)
    rss = RssGenerator(url_for('.tags', tag_id=tag.id), tag.writing, title=u"Contriver' {} Feed".format(tag.tag))
    return make_response(rss.rss_str())


@www.route('/masthead/')
def masthead():
    return render_template('static.html', static_title='Masthead', content=aopen('masthead.md'))


@www.route('/subscribe/')
def subscribe():
    return redirect(url_for('www.support'))


@www.route('/support/')
def support():
    return render_template('support.html')


@www.route('/search/', methods=('POST', 'GET'), defaults={'page': 1})
@www.route('/search/p/<int:page>/')
def search(page=None):
    form = SearchForm()
    if form.validate_on_submit():
        # TODO: preprocess the search term?
        query_term = form.data['search_term']
        results = search_query(query_term, page)
        current_app.logger.debug(results.items)

        return render_template(
            'search.html',
            paginated=results,
            search=SearchForm(placeholder=query_term))
    # return a blank search page
    else:
        return render_template('search.html')


#
# Error Handlers
#

@www.app_errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error), 404

@www.app_errorhandler(500)
def server_fault(error):
    return render_template('error.html', error=error), 500

#
# Redirects from v1
#

@www.route('/catalog/')
def redirect_catalog():
    """ redirect old urls to new ones

    Redirect the old url_map to the new one

    /catalog/ --> /
    /catalog/?filter=articles --> /articles/
    /catalog/?filter=reviews --> /reviews/
    /catalog/?filter=BLARG --> /
    """
    if 'filter' in request.args and \
        request.args['filter'] in ['articles', 'reviews']:
        target = request.args['filter']
        return redirect(url_for('www.' + target))
    else:
        return redirect(url_for('www.index'))

@www.route('/favicon.ico')
def favicon():
    """Redirect a /favicon.ico request to the static images file."""
    return(current_app.send_static_file('images/favicon.ico'))

@www.route('/sitemap.xml')
def sitemap():
    """ Create a sitemap
    http://www.sitemaps.org/protocol.html
    """
    pages = []
    RuleTuple = namedtuple('Rule', ['loc', 'lastmod',]) #'changefreq', 'priority'])
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()

    # static pages
    for rule in current_app.url_map.iter_rules():
        # Only process rules in this Blueprint
        # Only process GET methods
        # Only process endpoints without arguments
        if 'www' in rule.endpoint and "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(RuleTuple(rule.rule, ten_days_ago))

    # user model pages
    writings = db.session.query(_poly).filter_by(hidden=False).order_by(_poly.last_edited_date.desc()).all()
    print writings
    for article in writings:
        url = article.make_url() # url_for('www.articles', article_id=article.id )
        modified_time = article.last_edited_date.date().isoformat()
        pages.append(RuleTuple(url, modified_time))

    authors = db.session.query(Author).filter_by(hidden=False).all()
    for author in authors:
        pages.append(RuleTuple(url_for('www.authors', author_id=author.id), ten_days_ago))


    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response= make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response
