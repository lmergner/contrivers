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

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from flask.ext.login import UserMixin
from ..core import db
from werkzeug import generate_password_hash, check_password_hash

from sqlalchemy.ext.declarative import declarative_base

__models__ = ['Admin']
# Base = declarative_base()
Base = db.Model
salt_phrase = 'f64a80d7b499472ea253f36b9b8b36ba'  # uuid.uuid4().hex

class Admin(Base, UserMixin):
    """ Main admin / user class """
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    #permissions = Column(Integer, nullable=True)

    def __repr__(self):
        return "<Admin: %s>" % self.username

    def __str__(self):
        return '{}'.format(self.username)

    def __unicode__(self):
        return u'{}'.format(self.username)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, passwd):
        return check_password_hash(self.password, passwd)


# class Address(Base):
#     __tablename__ = 'addresses'
#     id = Column('id', Integer, primary_key=True)
#     street = Column('street', String)
#     po_box = Column('po_box', String)
#     city = Column('city', String)
#     state = Column('state', String)
#     zip_code = Column('zip', String)


# class Contact(Base):
#     __tablename__ = 'contacts'
#     id = Column('id', Integer, primary_key=True)
#     first_name = Column('first_name', String)
#     last_name = Column('last_name', String)
#     email = Column('email', String, nullable=False, unique=True)
#     address_id = Column('address_id', Integer, ForeignKey('addresses.id'))
    # last_contacted = Column(DateTime)


# class Company(Base):
#     __tablenname__ = 'companies'
#     id = Column('id', Integer, primary_key=True)
#     name = Column('name', String, nullable=False, unique=True)
#     address_id = Column('address_id', Integer, ForeignKey('addresses.id'))
#     phone = Column('phone', String)

__models__ = (Admin)
