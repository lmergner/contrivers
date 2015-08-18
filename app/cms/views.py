#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    app.cms.views
    -------------

    Url endpoints for cms including /login and /logout.
"""


from flask import (
    flash, render_template, g, session,
    redirect, url_for, request, current_app
    )
from flask.ext.login import (
    login_required, login_user, logout_user
    )
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound

from ..core import login_manager, db
from . import cms
from .models import Editor
from .forms import LoginForm

@cms.route('/login', methods=['GET', 'POST'])
def login():
    # if g.user is not None and g.user.is_authenticated():
    #     return redirect(request.args.get('next') or '.')
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        try:
            # TODO: Handle logins by email
            editor = Editor.query.\
                    filter_by(username=form.username.data).\
                    first()
        except NoResultFound:
            current_app.logger.info("{}: Invalid username.".format(form.username.data))
            flash('No user found with that username.')
            redirect(url_for('.login'))
        if editor.verify_password(form.password.data):
            flash("User logged in.")
            current_app.logger.info("{} logged in.".format(editor.username))
            login_user(editor, remember=True)
            return redirect(request.args.get("next") or '/cms/')  # url_for('.editor'))
        else:
            flash("Password incorrect")
    else:
        return render_template('login.html', form=form)


@cms.route('/logout')
@login_required
def logout():

    current_app.logger.info("{} logged in.".format(editor.username))
    logout_user()
    return redirect(url_for('www.index'))


@login_manager.user_loader
def load_user(editor_id):
    try:
        return db.session.query(Editor).get(editor_id)
    except OperationalError:
        return None
