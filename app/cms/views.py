#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright © 2014 Luke Thomas Mergner <lmergner@gmail.com>
#
# Distributed under terms of the MIT license.
"""
    app.cms.views
    -------------

    Url endpoints for cms including /login and /logout.
"""


from flask import (
    flash, render_template,
    redirect, url_for, request, current_app
    )
from flask.ext.login import (
    login_required, login_user, logout_user
    )
from sqlalchemy.exc import OperationalError

from ..core import login_manager, db
from . import cms
from .forms import LoginForm
from .models import *


def validate_user(username, password):
    """Query by name and validate the password"""
    admin = db.session.query(Admin).filter_by(username=username).one()
    if admin.verify_password(password):
        return True
    return False


@cms.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = db.session.query(Admin).filter(
            Admin.username == form.username.data).first()
        if admin.verify_password(form.password.data):
            flash("User logged in.")
            current_app.logger.debug("{} logged in.".format(admin.username))
            login_user(admin, remember=True)
            return redirect(request.args.get("next") or '/admin/')  # url_for('.admin'))
        else:
            flash("Password incorrect")
    else:
        return render_template('login.html', form=form)


@cms.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('www.index'))


@login_manager.user_loader
def load_user(userid):
    try:
        return db.session.query(Admin).get(userid)
    except OperationalError:
        return None


#### CMS CRUD via Angular

@login_required
@cms.route('/')
def index():
    return render_template('cms_layout.html')
