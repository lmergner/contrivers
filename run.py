#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
run
===

Create a testing environment for a flask app using
Python's `argparse` module. The CLI takes subcommands--
run and create--the second of which will populate a db
with some test data.

"""

from __future__ import print_function  # Suppress pylint errors
import os
import argparse
try:
    from livereload import Server
except ImportError:
    pass
from app import create_app


def setup_debug_toolbar(app, redirect=True):
    """ Conditionally import and load the Flask Debuging Toolbar """
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = redirect
    try:
        from flask_debugtoolbar import DebugToolbarExtension
        return DebugToolbarExtension(app)
    except ImportError:
        print("Could not import DebugToolbarExtension")


def export_env():
    """ Open an .env file and load it into the os.environ """
    print("Loading the local .env file")
    with open('./.env') as f:
        for line in f.readlines():
            key, value = line.strip().split('=')
            os.environ[key] = value


def parse_remainder(strings):
    """ Return a dict of key=value pairs from argparse.REMAINDER """
    cfg = {}
    for pair in strings:
        if pair == '--':
            continue
        key, value = pair.split('=')
        cfg[key.upper()] = value
    return cfg


parser = argparse.ArgumentParser(prog='test server')

parser.add_argument(
    '--host',
    help='Specify an alternative to localhost.',
    default='0.0.0.0:8000'
)

parser.add_argument(
    '-t', '--testing',
    action='store_true',
    default=False,
    help="Enable the app with the testing flag True."
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Enable debugging'
)

parser.add_argument(
    '--no-reload',
    action='store_false',
    default=True,
    help='Turn off auto reloading.'
)

parser.add_argument(
    '--no-bar',
    action='store_true',
    help='disable the toolbar with debug on.'
)

parser.add_argument(
    '--live-reload',
    action='store_true',
    help='Run with livereload server.'
)

parser.add_argument(
    '--blueprints',
    '-b',
    nargs='*',
    help='Specify blueprints to be loaded at runtime.'
)

parser.add_argument(
    '--list-blueprints',
    action='store_true',
    help='List current default blueprints.'
)

parser.add_argument(
    '--use-env',
    '-e',
    action='store_true',
    help='Load the ./.env file os.environ',
)

parser.add_argument(
    'config_vars',
    nargs=argparse.REMAINDER,
    help='Load config values at runtime, bypassing the config file or env file'
)

if __name__ == '__main__':
    args = parser.parse_args()

    if args.use_env:
        export_env()

    if args.list_blueprints:
        from app import default_blueprints
        print('\nCurrently installed Blueprints...')
        for bp in default_blueprints:
            print('\t{}'.format(bp))
        raise SystemExit

    if args.blueprints:
        blueprints = args.blueprints
    else:
        blueprints = None

    if args.config_vars:
        config_vars = parse_remainder(args.config_vars)
    else:
        config_vars = {}

    # Now setup and run the application
    app = create_app(
        'contrivers-cli-runner',
        debug=args.debug,
        testing=args.testing,
        blueprints=blueprints,
        additional_config_vars=config_vars
    )

    # Disable the Debug toolbar with a flag
    if not args.no_bar:
        setup_debug_toolbar(app, args.testing)

    host, port = args.host.split(':')
    port = int(port)

    # Flag for loading live_reload
    if args.live_reload:
        server = Server(app.wsgi_app)
        server.watch('app/')
        server.serve(host=host, port=port)
    else:
        app.run(use_reloader=args.no_reload, host=host, port=port)
