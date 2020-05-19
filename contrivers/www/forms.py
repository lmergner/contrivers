#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    contrivers.www.forms
    -------------

    Web forms via WTForms.
"""

from flask_wtf import FlaskForm
from wtforms import TextField

class SearchField(TextField):
    # Should set type to 'search' for css selectors
    pass


class SearchForm(FlaskForm):
    search_term = TextField("Search")