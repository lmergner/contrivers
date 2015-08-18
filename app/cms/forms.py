#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, validators, BooleanField)


class LoginForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [validators.Required()])
    remember_me = BooleanField('remember_me', default=False)
