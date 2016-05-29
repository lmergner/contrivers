#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 lmergner <gmail.com>
#
# Distributed under terms of the MIT license.

"""
    contrivers.app
    --------------

    SubClass of the main Flask class so that we can use a custom jinja2
    template loader.

"""

import os

from flask import current_app, Flask
from flask.helpers import locked_cached_property
from jinja2 import BaseLoader, ChoiceLoader, TemplateNotFound, FileSystemLoader

from .core import Template
from .core import db

class DatabaseLoader(BaseLoader):
    """ Load templates from a database """

    def __init__(self, db):
        # Flask-Sqlalchemy db object
        self._db = db

    def get_source(self, environment, template):
        _q = self._db.session.query
        try:
            # Every render_template call should be within
            # a request context
            result = _q(Template).filter_by(filename=template).one()
            return result.html.decode('utf-8')
        except:
            if current_app.debug:
                current_app.logger.debug('Template {} not found in database.'.format(template))
            raise TemplateNotFound(template)


class ContriversFlask(Flask):
    """ Subclass base Flask app to overload the
    jinja template loader."""

    @locked_cached_property
    def jinja_loader(self):
        """ Return a jinja2 ChoiceLoader that checks the database,
        then the filesystem template directory."""
        return ChoiceLoader([
            FileSystemLoader(os.path.join(self.root_path, self.template_folder)),
            DatabaseLoader(db) ])


