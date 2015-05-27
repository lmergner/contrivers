#/usr/bin/env python
#! -*- coding: utf-8 -*-
"""

    app.www.queries
    ---------------

    Collect queries in one module for logging, tuning, and refactoring
"""

from contextlib import contextmanager

from flask import request, session, current_app, abort
from sqlalchemy import func, desc
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from flask.ext.sqlalchemy import Pagination
from sqlalchemy.orm import with_polymorphic

from ..core import *
from ..core.models import tag_to_writing

__all__ = [
    'get_current_issue','get_featured',
    'base_query', 'paginate', '_poly'
    ]

_q = db.session.query
_poly = with_polymorphic(Writing, [Article, Review])

# a non-bound paginate function for polymorphic queries
def paginate(query, page, per_page=20, error_out=True):
    """Returns `per_page` items from page `page`.  By default it will
    abort with 404 if no items were found and the page was larger than
    1.  This behavor can be disabled by setting `error_out` to `False`.
    Returns an :class:`Pagination` object.

    https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy/__init__.py
    """
    if error_out and page < 1:
        abort(404)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    if not items and page != 1 and error_out:
        abort(404)

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = query.order_by(None).count()

    return Pagination(query, page, per_page, total, items)



def id_query(model, _id, check_none=True):
    """ Search by id and handle exceptions """
    try:
        rs = db.session.query(model).get(_id)
        if rs is None:
            abort(404)
        return rs

    except NoResultFound, e:
        current_app.logger.error(e)
        abort(404)
    except OperationalError, e:
        current_app.logger.error(e)
        abort(500)
    except MultipleResultsFound, e:
        current_app.logger.error(e)
        abort(500)


def page_query(model, page, query=None):
    """ Paginated query and handle exceptions """
    try:
        if query is None:
            return paginate(db.session.query(model), page)
        else:
            return paginate(query, page)

    except NoResultFound, e:
        current_app.logger.error(e)
        abort(404)
    except OperationalError, e:
        current_app.logger.error(e)
        abort(500)
    except MultipleResultsFound, e:
        current_app.logger.error(e)
        abort(500)


def index_query():
    try:
        featured = db.session.query(_poly).order_by(_poly.publish_date.desc()).filter_by(featured=True, hidden=False).all()
        # curr_issue = db.session.query(Issue).order_by(Issue.issue_num.desc()).first()
        curr_issue = { 'articles' :
                db.session.query(_poly).order_by(_poly.publish_date.desc()).filter_by(featured=False, hidden=False).limit(5)
                }
        return featured, curr_issue
    except NoResultFound, e:
        current_app.logger.error(e)
        abort(404)
    except OperationalError, e:
        current_app.logger.error(e)
        abort(500)
    except MultipleResultsFound, e:
        current_app.logger.error(e)
        abort(500)


def search_query(search_term, page):
    try:
        return paginate(db.session.query(_poly).filter(Writing.tsvector.op('@@')(func.plainto_tsquery(search_term))), page)
    except NoResultFound, e:
        current_app.logger.error(e)
        abort(404)
    except OperationalError, e:
        current_app.logger.error(e)
        abort(500)
    except MultipleResultsFound, e:
        current_app.logger.error(e)
        abort(500)

def tag_query(page):
    query = db.session.query(Tag, func.count(tag_to_writing.c.writing_id).label('total')).join(tag_to_writing).group_by(Tag).order_by('total DESC').all()
    # query = db.session.query(Tag).join(tag_to_writing).order_by(func.count(tag_to_writing.c.writing_id))
    results = page_query(Tag, page, query=query)
    for tag in results.items:
        tag.total = len(tag.writing)
    return results

