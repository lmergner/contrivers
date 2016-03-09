# -*- coding: utf-8 -*-
"""
    app.core.meta
    -------------

    Metaclasses and Mixins for app.core.models

"""

import datetime

import pytz
from werkzeug import cached_property
from flask import url_for, current_app
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import synonym

# TODO: remove all timezones and store dates as UTC w/o datetimes
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
    _create_date = Column(
        'create_date',
        DateTime(timezone=True),
        nullable=False,
        default=datetime_with_timezone
    )
    _last_edited_date = Column(
        'last_edited_date',
        DateTime(timezone=True),
        onupdate=datetime_with_timezone,
        default=datetime_with_timezone
    )

    def get_create_date(self):
        return self._create_date.replace(tzinfo=pytz.utc)

    def set_create_date(self, value):
        self._create_date = value

    @declared_attr
    def create_date(cls):  # pylint: disable=no-self-argument
        return  synonym(
            '_create_date',
            descriptor=property(cls.get_create_date, cls.set_create_date))

    def get_last_edited_date(self):
        return self._last_edited_date.replace(tzinfo=pytz.utc)

    def set_last_edited_date(self, value):
        self._last_edited_date = value

    @declared_attr
    def last_edited_date(cls):  # pylint: disable=no-self-argument
        return  synonym(
            '_last_edited_date',
            descriptor=property(cls.get_last_edited_date, cls.set_last_edited_date))


class PublishMixin(object):
    # Only writing has a publish date
    _publish_date = Column(
            'publish_date', DateTime(timezone=True))

    def get_publish_date(self):
        if self._publish_date is None:
            return None
        else:
            return self._publish_date.replace(tzinfo=pytz.utc)

    def set_publish_date(self, value):
        self._publish_date = value

    @declared_attr
    def publish_date(cls):  # pylint: disable=no-self-argument
        return synonym(
            '_publish_date',
            descriptor=property(cls.get_publish_date, cls.set_publish_date))


class JsonMixin(object):
    """ Mixin ABC that provides a jsonify method """

    @cached_property
    def jsonify(self):
        return {}  # json serializable dict

    serialize = jsonify


class UrlMixin(object):
    """ Mixin that provides url method for models with type and id properties
    """
    slug = None
    default_view_blueprint = 'www'
    default_route = 'archive'

    def url(self):
        """ return a valid url from model type and id """
        route = '.'.join((self.default_view_blueprint, self.route or self.default_route))
        if self.id is None:
            return url_for(route, _external=True)

        # Use kw expansion so we can optionally set the slug
        params = {'id_': self.id}

        # Don't pass the slug to url_for if it isn't set or ''
        if self.slug is not None and self.slug != '':
            params['slug'] = self.slug

        return url_for(route, _external=True, **params)

    make_url = url  # alias
