#-*- codeing: utf-8 -*-

from flask.ext.admin import expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user
from flask import url_for, current_app
from wtforms.fields import TextAreaField, SelectField
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
    column_exclude_list = ['text', 'abstract', 'tsvector']
    column_sortable_list = ['title', 'create_date', 'featured', 'hidden', 'respondees']
    column_hide_backrefs = True
    form_excluded_columns = ['create_date', 'type']
    form_overrides = dict(
            text=TextAreaField,
            summary=TextAreaField,)


class ArticleView(WritingView):
    pass

class ReviewView(WritingView):
    pass

class AuthorView(AuthMixin, ModelView):
    column_exclude_list = ['bio', 'twitter', 'email']

class BookView(AuthMixin, ModelView):
    column_exclude_list = ['city', 'year', 'isbn_10', 'isbn_13', 'pages', 'price']

class TemplateView(AuthMixin, ModelView):
    form_overrides = dict(
        html=TextAreaField
        )


admin.name = 'CMS'
# admin.index_view = IndexView()

admin.add_view(ArticleView(Article, db.session))
admin.add_view(ReviewView(Review, db.session))

admin.add_view(IssueView(Issue, db.session))
admin.add_view(AuthorView(Author, db.session))
admin.add_view(TagView(Tag, db.session))
admin.add_view(BookView(Book, db.session))
admin.add_view(TemplateView(Template, db.session))

