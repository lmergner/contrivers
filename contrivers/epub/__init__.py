#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 Luke Thomas Mergner <lmergner@gmail.com>
#
# Distributed under terms of the MIT license.

"""
    app.epub

    ebook generator
"""

import datetime, uuid
from jinja2 import Environment, FileSystemLoader

class Title(object):

    def __init__(self, title):
        self.title = title
        self.id = None
        self.title_types = ('main', 'subtitle', 'short', 'collection', 'edition', 'extended')

        # Sequence in which the title should be displayed in relation to other titles
        self.display_seq = None

        # Alphabetized title
        self.file_as = u"Title, The"


class Identifier(object):

    def __init__(self, ident_type):
        if ident_type not in ('uuid', 'isbn', 'doi'):
            raise ValueError("Identifier must be one of uuid, isbn, or doi.")
        self.ident_type = ident_type
        self.ident = None


class Creator(object):

    def __init__(self):
        self.name


class EbookItem(object):

    def __init__(self):
        self.valid_media_types = ('application/xhtml+xml')
        self.valid_linear = ('yes', 'no')

        self.href = None
        self.idref = None
        self.linear = 'yes'
        self.properties = None  # that can specify whether the given content document starts on the left or right side of a spread


class Ebook(object):

    def __init__(self, template_path='./templates/'):
        self.title
        self.language
        self.publish_date
        self.creator # main attribution
        self.description
        self.publisher
        self.source

        self.modified_timestamp = datetime.datetime.now().isoformat()  # 2011-01-01T12:00:00Z
        self.identifier = Identifier('uuid')

        self.jinja_environment = Environment(loader=FileSystemLoader(template_path))

        self.manifest = []
        self.cover_image
        self.nav
        self.valid_alerts = ('mathml', 'scripted', 'svg', 'remote-resources', 'switch')

    def register(self, item):
        self.manifest.append(item)


