#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    contrivers.www.views
    ----------------

"""
from datetime import datetime, timedelta
from collections import namedtuple

from flask import (
    render_template, request, url_for, redirect, make_response, abort,
    current_app, g
)
from sqlalchemy import desc, func
from .forms import SearchForm
from .rss import RssGenerator
from . import www
from ..models import Writing, Article, Review, Tag, Author, db, Reading
from ..utils import aopen


@www.context_processor
def set_site_info():
    return dict(search=SearchForm())

# @cache.cached(timeout=50)
@www.route('/')
def index():
    """ return the index page """
    return render_template(
        'index.html',
        featured=Writing.query.\
                order_by(Writing.publish_date.desc()).\
                filter_by(featured=True, hidden=False).\
                all(),
        articles=Writing.query.\
                order_by(Writing.publish_date.desc()).
                filter_by(featured=False, hidden=False).\
                limit(5),
        rss_url=url_for('.rss_index', _external=True))

@www.route('/rss/')
def rss_index():
    rss = RssGenerator(
        url_for('.index', _external=True),
        Writing.query.\
            filter_by(hidden=False).\
            order_by(Writing.publish_date.desc()).\
            limit(20))
    return make_response(rss.rss_str())

@www.route('/articles/featured/<int:page>/')
@www.route('/articles/featured/', defaults={'page': 1})
def featured(page):
    featured = Writing.query.\
        filter_by(featured=True).\
        order_by(Writing.publish_date).\
        paginate(page)
    return render_template(
        'articles.html',
        paginated = featured,
        endpoint='.featured',
        rss_url = url_for('.rss_featured', _external=True))

@www.route('/articles/featured/rss/')
def rss_featured():
    rss = RssGenerator(
        url_for('.featured', _external=True),
        Writing.query.filter_by(featured=True, hidden=False).order_by(Writing.publish_date.desc()).limit(10),
        title=u"Contrivers' Review Featured")
    return make_response(rss.rss_str())

@www.route('/articles/', defaults={'id_': None, 'page': 1, 'slug': None})
@www.route('/articles/<int:id_>/<slug>/', defaults={'page': 1})
@www.route('/articles/<int:id_>/', defaults={'page': None, 'slug': None})
@www.route('/articles/p/<int:page>/', defaults={'id_': None, 'slug': None})
def articles(id_, page, slug):
    if id_ is not None:
        return render_template(
            'article.html',
            article=Article.query.get_or_404(id_))
    else:
        return render_template(
            'articles.html',
            paginated=Article.query.order_by(Article.publish_date.desc()).paginate(page),
            endpoint='.articles',
            rss_url = url_for('.rss_articles', _external=True))

@www.route('/articles/rss/')
def rss_articles():
    query = Article.query.order_by(Article.publish_date).limit(20)
    rss = RssGenerator(url_for('.articles', _external=True), query, title=u"Contrivers’ Review Articles")
    return make_response(rss.rss_str())

@www.route('/reviews/', defaults={'id_': None, 'page': 1, 'slug': None})
@www.route('/reviews/<int:id_>/<slug>/', defaults={'page': 1})
@www.route('/reviews/<int:id_>/', defaults={'page': 1, 'slug': None})
@www.route('/reviews/p/<int:page>/', defaults={'id_': None, 'slug': None})
def reviews(id_, page, slug):
    if id_ is not None:
        return render_template(
            'article.html',
            article=Review.query.get_or_404(id_))
    else:
        return render_template(
            'articles.html',
            paginated=Review.query.order_by(Review.publish_date.desc()).paginate(page),
            endpoint='.reviews',
            rss_url = url_for('.rss_reviews', _external=True))

@www.route('/reviews/rss/')
def rss_reviews():
    rss = RssGenerator(
        url_for('.reviews'),
        Review.query.order_by(Review.publish_date.desc()).limit(20),
        title=u"Contrivers' Review Book Reviews")
    return make_response(rss.rss_str())

@www.route('/readings/', defaults={'id_': None, 'page': 1, 'slug': None})
@www.route('/readings/<int:id_>/<slug>/', defaults={'page': 1})
@www.route('/readings/<int:id_>/', defaults={'page': 1, 'slug': None})
@www.route('/readings/p/<int:page>/', defaults={'id_': None, 'slug': None})
def readings(id_, page, slug):
    if id_ is not None:
        return render_template(
            'article.html',
            article=Reading.query.get_or_404(id_))
    else:
        return render_template(
            'articles.html',
            paginated=Reading.query.order_by(Reading.publish_date.desc()).paginate(page),
            endpoint='.readings',
            rss_url = url_for('.rss_readings', _external=True))

@www.route('/readings/rss/')
def rss_readings():
    rss = RssGenerator(
        url_for('.readings'),
        reading.query.order_by(reading.publish_date.desc()).limit(20),
        title=u"Contrivers' reading Book readings")
    return make_response(rss.rss_str())


@www.route('/archive/', defaults={'page': 1})
@www.route('/archive/p/<int:page>/')
def archive(page):
    return render_template('articles.html',
        paginated=Writing.query.order_by(Writing.publish_date.desc()).paginate(page),
        endpoint='.archive',
        rss_url = url_for('.rss_reviews', _external=True))

@www.route('/archive/rss/')
def rss_archive():
    query = Writing.query.order_by(Writing.publish_date.desc()).limit(20)
    rss = RssGenerator(url_for('.archive', _external=True), query, title=u"Contrivers' Review Recent")
    return make_response(rss.rss_str())

@www.route('/authors/', defaults={'id_': None, 'page': 1, 'slug': None})
@www.route('/authors/<int:id_>/<slug>/', defaults={'page': 1})
@www.route('/authors/<int:id_>/', defaults={'page': 1, 'slug': None})
@www.route('/authors/p/<int:page>/', defaults={'id_': None, 'slug': None})
def authors(id_, page, slug):
    if id_ is not None:
        # TODO: paginate list of single author's articles
        author = Author.query.get_or_404(id_)
        return render_template(
            'author.html',
            page_type='authors',
            author=author,
            rss_url=url_for('.rss_author', id_=author.id, _external=True))
    else:
        return render_template(
            'authors.html',
            paginated = Author.ordered_query(page=page),
            endpoint='.authors')

@www.route('/authors/<int:id_>/rss/')
def rss_author(id_):
    author = Author.query.get_or_404(id_)
    rss = RssGenerator(url_for('.authors', author_id=author.id), author.writing, title=u"{} -- Contrivers' Review".format(author.name))
    return make_response(rss.rss_str())

@www.route('/categories/', defaults={'id_': None, 'page': 1, 'slug': None})
@www.route('/categories/<int:id_>/<slug>/', defaults={'page': 2})
@www.route('/categories/<int:id_>/', defaults={'page': 1, 'slug': None})
@www.route('/categories/p/<int:page>/', defaults={'id_': None, 'slug': None})
def tags(id_, page, slug):
    if id_ is not None:
        # TODO: paginate list of single tag's articles
        tag = Tag.query.get_or_404(id_)
        return render_template(
            'tag.html',
            tag=tag,
            rss_url=url_for('.rss_tag', id_=tag.id, _external=True))
    else:
        return render_template(
            'tags.html',
            paginated=Tag.ordered_query(page=page))

@www.route('/categories/<int:id_>/rss/')
def rss_tag(id_):
    tag = Tag.query.get_or_404(id_)
    rss = RssGenerator(
        url_for('.tags', id_=tag.id),
        tag.writing,
        title=u"Contrivers\' Review -- {}".format(tag.tag))
    return make_response(rss.rss_str())

@www.route('/masthead/')
def masthead():
    return render_template('static.html', static_title='Masthead', content=aopen('masthead.md', bucket_name=current_app.config.get('BUCKET')))

@www.route('/support/')
def support():
    return render_template('support.html')

# @www.route('/readings/')
# def readings():
#     return redirect(url_for('www.tags', id_=6, page=1))

@www.route('/search/', methods=('POST', 'GET'), defaults={'page': 1})
@www.route('/search/p/<int:page>/')
def search(page):
    form = SearchForm()
    if form.validate_on_submit():
        # TODO: preprocess the search term?
        g.search_term = form.data['search_term']
        results = Writing.query.\
            filter(Writing.tsvector.op('@@')(
                func.plainto_tsquery(form.data['search_term']))).\
            paginate(page)

        return render_template(
            'search.html',
            paginated=results,
            search=SearchForm(placeholder=form.data['search_term']))
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
    /catalog/?filter=BLARG --> abort(404)
    """
    if 'filter' in request.args and \
        request.args['filter'] in ['articles', 'reviews']:
        target = request.args['filter']
        return redirect(url_for('www.' + target))
    else:
        return redirect(url_for('www.index'))
        # return abort(404)

@www.route('/subscribe/')
def subscribe():
    """ Redirect the old subscribe endpoint to the new support endpoint"""
    return redirect(url_for('www.support'))

@www.route('/article/<int:id>/')
@www.route('/article/', defaults={'id': None})
def redirect_article(id):
    return redirect(url_for('.articles', id_=id))

#
# Redirects from v2
#
@www.route('/issues/', defaults={'issue_id': None, 'page': 1})
@www.route('/issues/p/<int:page>/', defaults={'issue_id': None})
@www.route('/issues/<int:issue_id>/', defaults={'page': 1})
def issues(issue_id, page=1):
    """ No more issues """
    return redirect(url_for('www.index'))

@www.route('/featured/')
def redirect_featured():
    return redirect(url_for('www.featured'))

## END REDIRECTS

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
    writings = Writing.query.\
            filter_by(hidden=False).\
            order_by(Writing.last_edited_date.desc()).\
            all()
    for article in writings:
        url = article.make_url() # url_for('www.articles', article_id=article.id )
        modified_time = article.last_edited_date.date().isoformat()
        pages.append(RuleTuple(url, modified_time))

    authors = Author.query.filter_by(hidden=False).all()
    for author in authors:
        pages.append(RuleTuple(author.url(), ten_days_ago))


    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response
