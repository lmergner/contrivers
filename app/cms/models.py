#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright © 2014 Luke Thomas Mergner <lmergner@gmail.com>
#
# Distributed under terms of the MIT license.

"""
    app.cms.models
    --------------

    SQLAlchemy models for managing content.
"""

from flask import current_app
from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from flask.ext.login import UserMixin
from passlib.context import CryptContext

from ..core.ext import db
from ..core.models import Author
from ..core.errors import ModelError
from ..core.mixins import DatesMixin, datetime_with_timezone

# pbkdf2_sha1 appears to be what werkzeug.security.generate_password_hash uses
pass_context = CryptContext(
    schemes=[ 'bcrypt', ],
    default='bcrypt',
    bcrypt__min_rounds=13)


class Editor(UserMixin, DatesMixin, db.Model):
    """ Editors can login and manage the content """
    __tablename__ = 'editors'
    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(50))
    email = Column('email', String(50), unique=True, nullable=False)
    password = Column('password', String(100), nullable=False)
    password_updated = Column('password_updated', DateTime(timezone=False))

    # Link to author table in case we have editors that are also
    # authors
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref=backref('editor_ident', uselist=False))

    # Permissions define what powers an editor has
    #permissions = Column(Integer, nullable=True)

    def __init__(self, password=None, username=None, email=None, **kwargs):
        if password is None or email is None:
            raise ModelError('Admin must be created with a password and email')
        self.password = self.hash_password(password)
        self.username = username
        self.email = email
        super(Editor, self).__init__(**kwargs)

    def __repr__(self):
        return "<Admin: %s>" % self.username

    def __str__(self):
        return u'{}'.format(self.username)

    def hash_password(self, password):
        self.password = pass_context.encrypt(password)
        self._password_updated = datetime_with_timezone()

    def verify_password(self, password):
        valid, new_hash = pass_context.verify_and_update(password, self.password)
        if valid:
            if new_hash:
                current_app.logger.info('Updating password hash for user {}'.format(self.username))
                self.password = new_hash
                self._password_updated = datetime_with_timezone()
            return True
        else:
            return False
