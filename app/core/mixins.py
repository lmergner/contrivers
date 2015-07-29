# -*- coding: utf-8 -*-
"""
    app.core.meta
    -------------

    Metaclasses and Mixins for app.core.models

"""

import datetime

import pytz
from flask import url_for
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

def datetime_with_timezone():
    """ Return a timezone aware datetime object """
    return datetime.datetime.now(tz=pytz.utc)


class BaseMixin(object):
    """ Mixin for SQLA declarative orm classes

    Provides a default implementation for __tablename__, id, __repr__, __str__,
    and __unicode__
    """

    @declared_attr
    def __tablename__(cls):  # pylint: disable=E0213
        return cls.__name__.lower()  # + 's'

    id = Column('id', Integer, primary_key=True)

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self.id)

    def __str__(self):
        return self.__repr__().encode('utf-8')

    __unicode__ = __str__


class DatesMixin(object):
    """ Mixin for SQLAlchemy Models that track created date and last modified
    date.
    """
    create_date = Column(
        'create_date',
        DateTime(timezone=True),
        nullable=False,
        default=datetime_with_timezone
    )
    last_edited_date = Column(
        'last_edited_date',
        DateTime(timezone=True),
        onupdate=datetime_with_timezone,
        default=datetime_with_timezone
    )


class JsonMixin(object):
    """ Mixin ABC that provides a jsonify method """

    def jsonify(self):
        return {}  # json serializable dict

    @property
    def serialize(self):
        pass


class UrlMixin(object):
    """ Mixin that provides url method for models with type and id properties
    """

    def url(self):
        """ return a valid url from model type and id """
        _end = ''.join(['www.', self.type, 's'])
        _kw = self.type + '_id'
        _id = self.id
        kwargs = {_kw: _id}
        return url_for(_end, _external=True, **kwargs)

    make_url = url  # alias



