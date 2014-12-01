
#-*- coding: utf-8 -*-
"""
bootstrap.py
------------

A bootstrap script designed to be run from the heroku
shell. It focuses on adding Admin users to the postgresql
databse, listing them, or verifying their passwords.  It
can be run locally using the `--local` flag, however this
isn't of much help since your local run.py script should
be taking care of creating your test environment.

Right now it assumes a Flask app and app context
are needed to query the database. It assumes that
SQLAlchemy is used to query the database.

Todo: specify the model import path on the cli so the the
script can handle other people's User classes.

Author: Luke Thoams Mergner <lmergner@gmail.com>
License: Public Domain
"""


import argparse
import os
import cmd
import getpass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import auth, db, Admin

Base = db.Model

WELCOME = """
A Heroku bootstrap script for quickly adding
users to a sqlalchemy postgresql database.
"""

HELP = """
help    -> Print this message.
add     -> Add a new user to the database.
del     -> Remove a user from the database.
passwd  -> Change user password.
verify  -> Verify a users password.
list    -> Print all users.
drop    -> Drop tables from database.
bust    -> Attempt to bust the redis cache.
cache   -> List the redis cache keys.
exit    -> Quit
"""

HEROKU_HELP = """ If you are running on heroku already, try:
$ heroku config | grep HEROKU_POSTRESQL
$ heroku pg:promote HEROKU_POSTGRESQL_{color}_URL
"""

colors = {
    "info": '\033[92m',  # green
    "warn": '\033[93m',  # yellow
    "error": '\033[91m',  # red
    "end": '\033[0m'}


def passwd_loop():
    while True:
        try:
            passwd = getpass.getpass("Please input the base user password:  ")
            dbcheck = getpass.getpass("Please retype it:  ")
            if passwd == dbcheck:
                return passwd
            else:
                print("{}Passwords do not match, please retry.{}".format(
                    colors['error'], colors['end']))
        except KeyboardInterrupt:
            break


def add_user(username=None):
    if not username:
        username = raw_input("Please enter your username:  ")
    passwd = passwd_loop()
    user = Admin(username, passwd)
    with session_ctx() as session:
        session.add(user)
    # assert user.id


def del_user(username=None):
    if not username:
        username = raw_input("Please enter a user to delete: ")
    with session_ctx() as session:
        userls = session.query(Admin).filter_by(
            username=username).all()
        for user in userls:
            print('{}: {}'.format(user.id, user.username))


def cleanup(*args):
    """Cleanup database on program exit
       but only if we are local.
    """
    pass


class Bootstrap(cmd.Cmd):

    prompt = '> '
    intro = WELCOME

    def do_help(self, line):
        print HELP

    def do_exit(self, line):
        raise SystemExit(0)

    def do_bust(self, line):
        confirm = raw_input(
           'Please confirm that you want ' +\
           'to bust the redis cache:  ')
        if confirm.lower() != 'yes':
            print("Abording...")
            return
        print("Busting cache...")
        import redis
        from urlparse import urlparse
        redis_url = os.environ.get('REDISTOGO_URL')
        if redis_url is None:
            redis_url = 'redis://localhost:6379'
        url = urlparse(redis_url)
        rc = redis.StrictRedis(host=url.hostname, port=url.port, password=url.password)
        for key in rc.keys():
            print("Deleting... %s" % key)
            rc.delete(key)

    def do_cache(self, line):
        import redis
        from urlparse import urlparse
        redis_url = os.environ.get('REDISTOGO_URL')
        if redis_url is None:
            redis_url = 'redis://localhost:6379'
        url = urlparse(redis_url)
        rc = redis.StrictRedis(host=url.hostname, port=url.port, password=url.password)
        for key in rc.keys():
            print("%s" % key)

    def do_drop(self, line):
        confirm = raw_input(
            'Please confirm that you want ' + \
            'to drop all tables in the database: ')
        if confirm != 'yes':
            print("Aborting...")
            return
        print("Dropping all tables...")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def do_list(self, line):
        with session_ctx() as session:
            for adm in session.query(Admin).all():
                print('{uid}: {user:10}'.format(
                        uid=adm.id,
                        user=adm.username,
                        passwd=adm.password))

    def do_ls(self, line):
        self.do_list(line)

    def do_where(self, line):
        print('{}URL: {}{}'.format(colors['info'], colors['end'], url))

    def do_del(self, line):
        if line:
            has_spaces = line.split(' ')
            if len(has_spaces) > 1:
                print("{}Error:{} Usernames cannot contain spaces.".format(
                    colors['error'], colors['end']))
                return
        del_user(line.strip())

    def do_add(self, line):
        if line:
            has_spaces = line.split(' ')
            if len(has_spaces) > 1:
                print("{}Error:{} Usernames cannot contain spaces.".format(
                    colors['error'], colors['end']))
                return
        add_user(line.strip())

    def do_passwd(self, line):
        """Modify the password of an existing user."""
        if line:
            # take only the first word from the string
            uid = line.split()[0]
        else:
            # prompt for the username
            uid = raw_input("Enter username: ")

        # Get the Admin object from the database
        # using sqlalchemy.
        with session_ctx() as session:
            user = session.query(Admin).filter(
                Admin.username == uid).first()

        # If the result is None, end gracefully
        if user is None:
            print('Admin {}{}{} does not exist yet.'.format(
                colors['error'], uid, colors['end']))
            return

        # otherwise prompt for a new password
        # and hash it before saving
        user.hash_password(passwd_loop())

        print('was this hashed? {}'.format(user.password))
        with session_ctx() as session:
            session.commit()


    def do_verify(self, line):
        if line:
            uid  = line.split()[0]
        else:
            uid = raw_input("Enter username: ")

        with session_ctx() as session:
            user = session.query(Admin).filter(
                           Admin.username == uid).first()
            if user is None:
                print('Admin {}{}{} does not exist yet.'.format(
                    colors['error'], uid, colors['end']))
                return

        passwd = getpass.getpass("Password to verify: ")
        ver_string = "{c}{pw}{e} is the {ok} password"
        if user.verify_password(passwd):
            print(ver_string.format(
                    c  = colors['info'],
                    pw = passwd,
                    e  =  colors['end'],
                    ok = 'correct'))
        else:
            print(ver_string.format(
                c  = colors['warn'],
                pw = passwd,
                e  =  colors['end'],
                ok =  'incorrect'))

    def do_EOF(self, line):
        cleanup(db_fd)
        return True


class session_ctx(object):
    def __init__(self):
        self.session = Session()
        self.session._model_changes = {}

    def __enter__(self):
        return self.session

    def __exit__(self, *args):
        self.session.commit()
        self.session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='0.1dev')
    parser.add_argument('-e', '--echo', action='store_true')
    parser.add_argument('cmd', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    print(' ')

    try:
        url = os.environ.get('DATABASE_URL')
        assert url is not None
    except:
        print("{}This script is designed to work on heroku.{}".format(
            colors['warn'], colors['end']))
        print("{}".format(HEROKU_HELP))
        raise SystemExit("Database url is None")

    # setup straight sqlalchemy pipes
    engine = create_engine(url, echo=args.echo)
    # for now let's not use the scoped_session
    Session = sessionmaker(bind=engine)

    # make sure the database exists
    # its a bootstrap after all
    Base.metadata.create_all(engine)

    # if args were added to the command line
    # pass them to the cmd object as a string
    if args.cmd:
        Bootstrap().onecmd(' '.join(args.cmd))

    # otherwise run the normal cmdloop
    else:
        Bootstrap().cmdloop()
