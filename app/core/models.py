#-*- coding: utf-8 -*-
"""
    app.core.models
    ---------------

    SQLAlchemy ORM models


    Writing is polymorphic with Articles and Reviews
"""

import datetime

from flask import url_for
from sqlalchemy import (
    Integer, String, Column, ForeignKey, func,
    Table, Boolean, DateTime, Float,
    UniqueConstraint, CheckConstraint, event
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import TSVECTOR

from .ext import db

# alias for Flask-SQLAlchemy
Base = db.Model

def timestamp():
    """ Returns utcnow() but later we might want to change our timestamp """
    return datetime.datetime.utcnow()

__all__ = (
    'Tag', 'Author', 'Writing', 'Image', 'Book', 'Article', 'Review', 'Issue'
)

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
    return url_for(_end, _external=True, **kwargs)

# Many to Many :: Author to Article
author_to_writing = Table(
    'author_to_writing', Base.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('author_id', Integer, ForeignKey('author.id'))
)

# Many to Many :: Tag to Article
tag_to_writing = Table(
    'tag_to_writing', Base.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

# Many to Many Association Table linking Images to Writings
image_to_writing = Table(
    'image_to_writing', Base.metadata,
    Column('image_id', Integer, ForeignKey('image.id')),
    Column('writing_id', Integer, ForeignKey('writing.id'))
)

# Many to Many self-referential table for threaded responses
# http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-many-to-many-relationship
writing_to_writing = Table(
    'writing_to_writing', Base.metadata,
    Column('response_id', Integer, ForeignKey('writing.id'), primary_key=True),
    Column('respondee_id', Integer, ForeignKey('writing.id'), primary_key=True)
)


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

    @property
    def serialize(self):
        return { 'id': self.id, 'tag': self.tag,
                'articles': [article.id for article in self.writing] }


class Author(BaseMixin, Base):
    """Author table represents authors"""
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column('email', String, unique=True, nullable=False)
    twitter = Column('twitter', String, unique=True)
    bio = Column('bio', String)
    hidden = Column('hidden', Boolean, default=False)

    # Keep track of dates
    # create_date = Column(
    #     'create_date',
    #     DateTime(timezone=True), nullable=False,
    #     default=datetime.datetime.utcnow)
    # last_edited_date = Column(
    #     'last_edited_date',
    #     DateTime(timezone=True),
    #     onupdate=datetime.datetime.utcnow),
    #     default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self.email)

    def count(self):
        return len(self.writing)

    @property
    def serialize(self):
        return {
            'id': self.id, 'name': self.name, 'email': self.email,
            'twitter': self.twitter, 'bio': self.bio, 'hidden': self.hidden,
            'articles': [article.id for article in self.writing]
            }


class Issue(BaseMixin, Base):
    __tablename__ = 'issue'
    id = Column('id', Integer, primary_key=True)
    issue_num = Column('issue_num', Integer, unique=True)
    theme = Column('theme', String)
    articles = relationship('Writing', backref='issue')

    def __init__(self, autonumber=False, *args, **kwargs):
        if autonumber:
            kwargs['issue_num'] = self.auto_number()
        super(Issue, self).__init__(*args, **kwargs)

    def auto_number(self):
        """
        Return 1 + max issue_num

        We do not use a postgres sequence because we may want
        more control over the issue_num than a sequence would provide
        """
        max_num = db.session.query(func.max(Issue.issue_num)).scalar()
        if max_num is not None:
            return max_num + 1
        else:
            return 1

    def make_url(self):
        return url_for('www.issues', issue_id=self.id)

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
        DateTime(timezone=True), nullable=False,
        default=datetime.datetime.utcnow)
    last_edited_date = Column(
        'last_edited_date',
        DateTime(timezone=True),
        onupdate=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow)
    publish_date = Column('publish_date', DateTime(timezone=True))

    # track basic attributes of all writing:
    # title, text, summary
    title = Column(String, nullable=False)
    text = Column(String)
    abstract = Column('summary', String)

    # PostgreSQL Full Text Search field
    # http://www.postgresql.org/docs/current/static/datatype-textsearch.html
    tsvector = Column(TSVECTOR)

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
        backref=backref('writing', lazy='dynamic'))

    images = relationship('Image', secondary=image_to_writing,
        backref=backref('writing', lazy='subquery'))

    #
    # Response -> Adjacency List Relationship
    #

    responses = relationship("Writing",
                    secondary=writing_to_writing,
                    primaryjoin=id==writing_to_writing.c.response_id,
                    secondaryjoin=id==writing_to_writing.c.respondee_id,
                    backref='respondees'
                )

    def make_url(self):
        return _make_url_from_type(self)

    def __unicode__(self):
        return self.title.decode('utf-8')

    def __repr__(self):
        repr_date = self.publish_date if self.publish_date is None else ''
        return "<{}({} {})>".format(self.__class__.__name__, self.title, repr_date)

#
# Writing inherited models
#

class Article(Writing):
    __tablename__ = 'article'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'article'}

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'authors': [{'id': author.id, 'name': author.name} for author in self.authors],
            'text': self.text,
            'publish_date': self.publish_date.isoformat(),
            'create_date': self.create_date.isoformat(),
            'last_edited_date': self.last_edited_date.isoformat(),
            'featured': self.featured,
            'hidden': self.hidden,
            'issue_id': self.issue_id,
            'abstract': self.abstract,
            'tags': [tag.id for tag in self.tags],
            'images': None,
            'responses': [article.id for article in self.responses],
            'respondees': [article.id for article in self.respondees]
        }


class Review(Writing):
    __tablename__ = 'review'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'review'}
    book_reviewed = relationship('Book')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'authors': [author.id for author in self.authors],
            'text': self.text,
            'publish_date': self.publish_date.isoformat(),
            'create_date': self.create_date.isoformat(),
            'last_edited_date': self.last_edited_date.isoformat(),
            'featured': self.featured,
            'hidden': self.hidden,
            'issue_id': self.issue_id,
            'abstract': self.abstract,
            'tags': [tag.id for tag in self.tags],
            'images': None,
            'responses': [article.id for article in self.responses],
            'respondees': [article.id for article in self.respondees],
            'book_reviewed': self.book_reviewed.serialize
        }


class Book(BaseMixin, Base):
    __tablename__ = 'book'
    id = Column('id', Integer, primary_key=True)
    title = Column(String)
    subtitle = Column(String)
    author = Column(String)
    publisher = Column(String)
    city = Column(String)
    year = Column(Integer)
    isbn_10 = Column(
        'isbn_10',
        String(10),
        CheckConstraint('length(isbn_10) == 10', name='check_isbn_10_length'),
        unique=True
    )
    isbn_13 = Column(
        'isbn_13',
        String(13),
        CheckConstraint('length(isbn_13) == 13', name='check_isbn_13_length'),
        unique=True
    )
    pages = Column(Integer)
    price = Column(Integer)
    review_id = Column(Integer, ForeignKey('review.id'))
    translator = Column(String)
    editors = Column(String)
    edition = Column(String)

    UniqueConstraint(title, subtitle, author)

    def __unicode__(self):
        return self.title.decode('utf-8')

    @property
    def serialize(self):
        return {
            'id': self.id, 'title': self.title, 'author': self.author,
            'publisher': self.publisher, 'city': self.city, 'year': self.year,
            'isbn_10': self.isbn_10, 'isbn_13': self.isbn_13, 'pages': self.pages,
            'price': self.price, 'reviews': self.review_id
        }

