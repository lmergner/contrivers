#!/usr/bin/env python
#-*- coding: utf-8 -*-

# import uuid
from flask import (
    Blueprint, flash, render_template,
    redirect, url_for, request, current_app
    )
from flask.ext.login import (
    user_logged_in, login_required,
    UserMixin, login_user, logout_user
    )
from sqlalchemy.exc import OperationalError
from werkzeug import generate_password_hash, check_password_hash

from ..core import login_manager, db
from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, validators)


class LoginForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [validators.Required()])


auth = Blueprint('auth', __name__, template_folder='./templates')

salt_phrase = 'f64a80d7b499472ea253f36b9b8b36ba'  # uuid.uuid4().hex


__models__ = ['Admin']


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    # uuid = db.Column(GUID())

    def __init__(self, username, password):
        self.username = username
        self.hash_password(password)
        # self.uuid = uuid.uuid1()

    def __repr__(self):
        return "<Admin: %s>" % self.username

    def __str__(self):
        return unicode(self.username)

    def __unicode__(self):
        return u'%s' % self.username

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, passwd):
        return check_password_hash(self.password, passwd)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = db.session.query(Admin).filter(
            Admin.username == form.username.data).first()
        if admin.verify_password(form.password.data):
            flash("User logged in.")
            current_app.logger.debug("{} logged in.".format(admin.username))
            login_user(admin, remember=True)
            return redirect(request.args.get("next") or url_for('admin.index'))
        else:
            flash("Password incorrect")
    else:
        return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))


@login_manager.user_loader
def load_user(userid):
    try:
        return db.session.query(Admin).get(userid)
    except OperationalError:
        return None


def validate_user(username, password):
    admin = Admin.query.filter_by(username=username).one()
    if admin.verify_password(password):
        return True
    else:
        return False

