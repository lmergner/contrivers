#!/usr/bin/env python
"""
journal.models
==============

SQLAlchemy ORM models with some polymorphic stuff
"""

import datetime
import re
import json
import logging

import markdown
import translitcodec
from pytz import timezone

from flask import url_for
from sqlalchemy import (
    Integer, String, Column, ForeignKey,
    Table, Boolean, DateTime, event, Float, DDL)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.ext.hybrid import hybrid_property

from .ext import db
from .serializers import *

# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

# alias for Flask-SQLAlchemy
Base = db.Model

__all__ = [
    'Tag', 'Author', 'Writing',
    'Image', 'Book', 'Template',
    'Article', 'Review', 'Issue']

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def _make_url_from_type(obj):
    """ Make a valid url based on the polymorphic identity
    of the inherited class.  This is still an ugly solution, and I
    should probably just edit the queries to always join on the
    polymophic inheritance."""

    if not isinstance(obj, Writing):
        raise TypeError
    _end = 'www.' + obj.type + 's'
    _kw = obj.type + '_id'
    _id = obj.id
    kwargs = {_kw: _id}
    return url_for(_end, **kwargs)

# TimeZone Aware Datetime Objects
class TzDateTime(TypeDecorator):
    impl = DateTime

    def process_result_value(self, value, dialect):
        return localize_datetime(value)

def localize_datetime(dt):
    """Localize datetime objects to PST """
    tz = timezone('America/Los_Angeles')
    return tz.localize(dt)

# Many to Many :: Author to Article
author_to_writing = Table(
    'author_to_writing', Base.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('author_id', Integer, ForeignKey('author.id')))

# Many to Many :: Tag to Article
tag_to_writing = Table(
    'tag_to_writing', Base.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')))

# Many to Many Association Table linking Images to Writings
image_to_writing = Table(
    'image_to_writing', Base.metadata,
    Column('image_id', Integer, ForeignKey('image.id')),
    Column('writing_id', Integer, ForeignKey('writing.id')))

# Many to Many self-referential table for threaded responses
# http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-many-to-many-relationship
writing_to_writing = Table('writing_to_writing', Base.metadata,
    Column('response_id', Integer, ForeignKey('writing.id'), primary_key=True),
    Column('respondee_id', Integer, ForeignKey('writing.id'), primary_key=True))


class BaseMixin(object):
    """Provides str and repr functions for sqla
    objects."""

    def __repr__(self):
        return "<{} id: {}>".format(self.__class__.__name__, self.id)

    def __str__(self):
        return self.__repr__().encode('utf-8')


class Tag(BaseMixin, Base):
    """Tags represent categories or subjects"""
    __tablename__ = 'tag'
    id = Column('id', Integer, primary_key=True)
    tag = Column('name', String, unique=True)

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self.tag)

    def __hash__(self):
        return hash(''.join([self.__class__.__name__, str(self.id), self.tag]))

    @property
    def serialize(self):
        _serialize = Serializer(fields=['tag', 'id'])
        return _serialize(self)

    @hybrid_property
    def count(self):
        return len(self.writing)

    @count.expression
    def _count_expression(cls):
        return db.select([db.func.count(tag_to_writing.c.writing_id).label("writing_count")]).where(tag_to_writing.c.tag_id == cls.id).label("writing_count")


class Author(BaseMixin, Base):
    """Author table represents authors"""
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column('email', String, unique=True, nullable=False)
    twitter = Column('twitter', String, unique=True)
    bio = Column('bio', String)
    hidden = Column('hidden', Boolean, default=False)

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self.email)

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.id) + self.email)

    @property
    def serialize(self):
        _serialize = Serializer(fields=['id', 'email', 'twitter', 'bio', 'hidden', 'name'])
        return _serialize(self)


class Issue(BaseMixin, Base):
    __tablename__ = 'issue'
    id = Column('id', Integer, primary_key=True)
    issue_num = Column('issue_num', Integer, unique=True)
    theme = Column('theme', String)
    articles = relationship('Writing', backref='issue')

    def __unicode__(self):
        return self.theme.decode('utf-8')


class Image(BaseMixin, Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    url = Column(String)
    expired = Column(Boolean, default=False)


class Writing(BaseMixin, Base):
    """Base sqla class of all writing objects."""

    __tablename__ = 'writing'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'writing',
        'polymorphic_on': type
    }

    # Keep track of dates
    create_date = Column(
        'create_date',
        TzDateTime, nullable=False,
        default=localize_datetime(datetime.datetime.now()))
    last_edited_date = Column(
        'last_edited_date',
        TzDateTime,
        onupdate=localize_datetime(datetime.datetime.now()),
        default=datetime.datetime.now())
    publish_date = Column('publish_date', TzDateTime)

    # track basic attributes of all writing:
    # title, text, summary
    title = Column(String, nullable=False)
    text = Column(String)
    tsvector = Column(TSVECTOR)
    abstract = Column('summary', String)

    # track some tags that say if the piece is
    # publishable or if it should be highlighted in
    # some way
    hidden = Column(Boolean, nullable=False, default=True)
    featured = Column(Boolean, nullable=False, default=False)

    #
    # Relationships
    #

    issue_id = Column(Integer, ForeignKey('issue.id'))

    authors = relationship('Author', secondary=author_to_writing,
        backref=backref('writing', lazy='dynamic'))

    tags = relationship('Tag', secondary=tag_to_writing,
        backref=backref('writing', lazy='subquery'))

    images = relationship('Image', secondary=image_to_writing,
        backref=backref('writing', lazy='subquery'))

    #
    # Response -> Adjancy List Relationship
    #

    responses = relationship("Writing",
                    secondary=writing_to_writing,
                    primaryjoin=id==writing_to_writing.c.response_id,
                    secondaryjoin=id==writing_to_writing.c.respondee_id,
                    backref='respondees'
                )

    def __hash__(self):
        _key = ''.join([self.__class__.__name__, str(self.id), self.title])
        return hash(_key)

    def make_url(self):
        return _make_url_from_type(self)

    def __unicode__(self):
        return self.title.decode('utf-8')

    def __repr__(self):
        repr_date = self.publish_date if self.publish_date is None else ''
        return "<{}({} {})>".format(self.__class__.__name__, self.title, repr_date)



# Replace the ORM event with a Postgres trigger

# http://stackoverflow.com/questions/7888846/trigger-in-sqlachemy
# http://docs.sqlalchemy.org/en/rel_0_9/core/ddl.html#sqlalchemy.schema.DDL

tsv_ddl = DDL(
    "CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE " +\
    "ON writing FOR EACH ROW EXECUTE PROCEDURE " +\
    "tsvector_update_trigger(tsvector, 'pg_catalog.english', title, text);"
)
event.listen(Writing.__table__, 'after_create', tsv_ddl.execute_if(dialect='postgresql'))

#
# Writing inherited models
#

class Article(Writing):
    __tablename__ = 'article'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'article'}

    @property
    def serialize(self):
        _serialize = Serializer(fields=[
            'title', 'authors', 'text', 'publish_date', 'id',
            'create_date', 'last_edited_date', 'featured', 'hidden',
            'issue_id', 'abstract', 'tags', 'images', 'responses', 'respondees'
        ])
        return _serialize(self)


class Review(Writing):
    __tablename__ = 'review'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'review'}
    book_reviewed = relationship('Book')

    @property
    def serialize(self):
        _serialize = Serializer(fields=[
            'title', 'authors', 'text', 'publish_date', 'id',
            'create_date', 'last_edited_date',
            'featured', 'hidden', 'issue', 'abstract',
            'tags', 'images', 'responses', 'respondees', 'book_reviewed'
        ])
        return _serialize(self)


class Book(BaseMixin, Base):
    __tablename__ = 'book'
    id = Column('id', Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    author = Column(String)
    publisher = Column(String)
    city = Column(String)
    year = Column(Integer)
    isbn_10 = Column(Integer)
    isbn_13 = Column(String)
    pages = Column(Integer)
    price = Column(Float)
    review_id = Column(Integer, ForeignKey('review.id'))

    def __unicode__(self):
        return self.title.decode('utf-8')

    @property
    def serialize(self):
        pass


class Template(BaseMixin, Base):
    __tablename__ = 'template'
    id = Column('id', Integer, primary_key=True)
    filename = Column('filename', String, nullable=False)
    html = Column('html', String, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'html': self.html
        }


class KeyValueStore(Base):
    __tablename__ = 'key_value'
    key = Column(String, unique=True, primary_key=True)
    value = Column(JSON)

    @property
    def serialize(self):
        return self.value
