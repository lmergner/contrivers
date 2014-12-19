#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 Luke Thomas Mergner <lmergner@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""

from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, validators)


class LoginForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [validators.Required()])
