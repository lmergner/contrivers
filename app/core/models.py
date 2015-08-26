#-*- coding: utf-8 -*-
"""
    app.core.models
    ---------------

    SQLAlchemy ORM models


    Writing is polymorphic with Articles and Reviews
"""

from sqlalchemy import (
    Integer, String, Column, ForeignKey,
    Table, Boolean, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func

from .ext import db
from ..core.validators import validate_isbn
from .mixins import BaseMixin, DatesMixin, UrlMixin, PublishMixin


__all__ = (
    'Tag', 'Author', 'Writing', 'Image', 'Book', 'Article', 'Review'
)


# Many to Many :: Author to Article
author_to_writing = Table(
    'author_to_writing', db.Model.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('author_id', Integer, ForeignKey('author.id'))
)

# Many to Many :: Tag to Article
tag_to_writing = Table(
    'tag_to_writing', db.Model.metadata,
    Column('writing_id', Integer, ForeignKey('writing.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

# Many to Many Association Table linking Images to Writings
image_to_writing = Table(
    'image_to_writing', db.Model.metadata,
    Column('image_id', Integer, ForeignKey('image.id')),
    Column('writing_id', Integer, ForeignKey('writing.id'))
)

# reviewable_to_writing = Table(
#     'reviewable_to_writing', db.Model.metadata,
#     Column('reviewed_id', Integer, ForeignKey('reviewable.id')),
#     Column('review_id', Integer, ForeignKey('writing.id'))
# )

# Many to Many self-referential table for threaded responses
# http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#self-referential-many-to-many-relationship
writing_to_writing = Table(
    'writing_to_writing', db.Model.metadata,
    Column('response_id', Integer, ForeignKey('writing.id'), primary_key=True),
    Column('respondee_id', Integer, ForeignKey('writing.id'), primary_key=True)
)


class Tag(BaseMixin, UrlMixin, db.Model):
    """ Tags represent categories or subjects """
    tag = Column('name', String, unique=True)

    route = 'categories'

    @property
    def slug(self):
        return '-'.join(self.tag.lower().split())

    @property
    def count(self):
        cnt = func.count('*').label('cnt')
        return db.session.query(func.count('*')).\
                filter(self.id==tag_to_writing.c.tag_id).\
                scalar()

    @classmethod
    def ordered_query(self, page=1):
        """ Return a paginated query of all Tags ordered by count of writing """
        cnt = func.count('*').label('cnt')
        subq = db.session.query(self.id, cnt).\
                filter(self.id==tag_to_writing.c.tag_id).\
                group_by(self.id).\
                subquery()
        return self.query.\
                outerjoin(subq, self.id == subq.c.id).\
                order_by(subq.c.cnt.desc(), self.tag).\
                paginate(page)


class Author(BaseMixin, UrlMixin, db.Model):
    """ Author table represents authors """
    name = Column('name', String)
    email = Column('email', String, unique=True, nullable=False)
    twitter = Column('twitter', String, unique=True)
    bio = Column('bio', String)
    hidden = Column('hidden', Boolean, default=False)

    route = 'authors'

    @property
    def slug(self):
        trans_map = { ord('.'): None, ord(','): None}
        return '-'.join(self.name.lower().translate(trans_map).split())

    @property
    def count(self):
        cnt = func.count('*').label('cnt')
        return db.session.query(func.count('*')).\
                filter(self.id==author_to_writing.c.author_id).\
                scalar()

    @classmethod
    def ordered_query(self, page=1):
        """ Return a paginated query of all Authors ordered by count of writing """
        cnt = func.count('*').label('cnt')
        subq = db.session.query(self.id, cnt).\
                filter(self.id==author_to_writing.c.author_id).\
                group_by(self.id).\
                subquery()
        return self.query.\
                outerjoin(subq, self.id == subq.c.id).\
                order_by(subq.c.cnt.desc(), self.name).\
                paginate(page)


class Image(BaseMixin, db.Model):
    filename = Column(String)
    url = Column(String)
    expired = Column(Boolean, default=False)


class Writing(BaseMixin, DatesMixin, UrlMixin, PublishMixin, db.Model):
    """ db.Model sqla class of all writing objects. """

    # Must have id in the class definition otherwise
    # the adjecency list many-to-many freaks out
    id = Column('id', Integer, primary_key=True)

    # type is the polymorphic discriminator
    type = Column(String, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'writing',
        'polymorphic_on': type,
        'with_polymorphic': '*'
    }

    # track basic attributes of all writing:
    # title, text, summary
    title = Column('title', String, nullable=False)
    slug = Column('slug', String)
    text = Column('text', String)
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

    authors = relationship('Author', secondary=author_to_writing,
        backref=backref('writing', lazy='dynamic'))

    tags = relationship('Tag', secondary=tag_to_writing,
        backref=backref('writing', lazy='dynamic'))

    images = relationship('Image', secondary=image_to_writing,
        backref=backref('writing', lazy='subquery'))

    #
    # Response -> Adjacency List Relationship
    #

    responses = relationship(
        'Writing',
        secondary=writing_to_writing,
        primaryjoin=id==writing_to_writing.c.response_id,
        secondaryjoin=id==writing_to_writing.c.respondee_id,
        backref='respondees'
    )

#
# Writing inherited models
#

class Article(Writing):
    route = 'articles'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'article'}


class Review(Writing):
    route = 'reviews'
    id = Column('id', ForeignKey('writing.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'review'}
    book_reviewed = relationship('Book')


class Book(BaseMixin, db.Model):
    title = Column(String)
    subtitle = Column(String)
    author = Column(String)
    publisher = Column(String)
    city = Column(String)
    year = Column(Integer)
    isbn_10 = Column(
        'isbn_10',
        String(10),
        CheckConstraint('length(isbn_10) = 10', name='check_isbn_10_length'),
        unique=True
    )
    isbn_13 = Column(
        'isbn_13',
        String(13),
        CheckConstraint('length(isbn_13) = 13', name='check_isbn_13_length'),
        unique=True
    )
    pages = Column(Integer)
    price = Column(Integer)
    review_id = Column(Integer, ForeignKey('review.id'))
    translator = Column(String)
    editors = Column(String)
    edition = Column(String)

    UniqueConstraint(title, subtitle, author)

    @validates('isbn_10')
    def validate_isbn_10(self, key, isbn):
        return validate_isbn(isbn, 10)

    @validates('isbn_13')
    def validate_isbn_13(self, key, isbn):
        return validate_isbn(isbn, 13)
