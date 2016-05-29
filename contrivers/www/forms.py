#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    contrivers.www.forms
    -------------

    Web forms via WTForms.
"""

from flask.ext.wtf import Form
from wtforms import TextField

class SearchField(TextField):
    # Should set type to 'search' for css selectors
    pass


class SearchForm(Form):
    search_term = TextField("Search")

