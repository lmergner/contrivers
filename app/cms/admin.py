#! /usr/bin/env python
#-*- coding: utf-8 -*-

from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user
from wtforms.fields import TextAreaField
from flask.ext.admin import Admin
from ..core.models import *
from ..core import db

admin = Admin()


class AuthMixin(object):
    """ Mixin to determine if user is authenticaed """
    def is_accessible(self):
        return current_user.is_authenticated()


class TagView(AuthMixin, ModelView):
    form_excluded_columns = ['articles', 'posts']


class IssueView(AuthMixin, ModelView):
    column_hide_backrefs = False
    form_overrides = dict(description=TextAreaField)


class WritingView(AuthMixin, ModelView):
    column_exclude_list = ['text', 'abstract', 'tsvector', 'publish_date', 'last_edited_date', 'create_date', 'type']
    column_sortable_list = ['title', 'create_date', 'featured', 'hidden', 'respondees']
    column_hide_backrefs = True
    form_excluded_columns = ['create_date', 'type']
    form_overrides = dict(
            text=TextAreaField,
            summary=TextAreaField,
            abstract=TextAreaField,)


class ArticleView(WritingView):
    pass

class ReviewView(WritingView):
    pass

class AuthorView(AuthMixin, ModelView):
    column_exclude_list = ['bio', 'twitter', 'email']
    form_overrides = dict(
        bio=TextAreaField
    )

class BookView(AuthMixin, ModelView):
    column_exclude_list = ['city', 'year', 'isbn_10', 'isbn_13', 'pages', 'price']



admin.name = 'CMS'
# admin.index_view = IndexView()

admin.add_view(ArticleView(Article, db.session))
admin.add_view(ReviewView(Review, db.session))

admin.add_view(IssueView(Issue, db.session))
admin.add_view(AuthorView(Author, db.session))
admin.add_view(TagView(Tag, db.session))
admin.add_view(BookView(Book, db.session))
