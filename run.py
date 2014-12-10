#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
run
===

Create a testing environment for a flask app using
Python's `argparse` module. The CLI takes subcommands--
run and create--the second of which will populate a db
with some test data.

"""

import argparse
from livereload import Server
from app import create_app

def setupToolbar(app, testing, redirect=True):
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = redirect
    try:
        from flask_debugtoolbar import DebugToolbarExtension
        return DebugToolbarExtension(app)
    except ImportError:
        print("Could not import DebugToolbarExtension")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='test server')
    parser.add_argument(
            '--host',
            help='Specify an alternative to localhost.',
            default='0.0.0.0:8000')
    parser.add_argument(
            '-t', '--testing',
            action='store_true',
            default=False,
            help="Enable the app with the testing flag True.")
    parser.add_argument(
            '-d', '--debug',
            action='store_true',
            help='Enable debugging')
    parser.add_argument(
            '--no-reload',
            action='store_false',
            default=True,
            help='Turn off auto reloading.')
    parser.add_argument(
            '--no-bar',
            action='store_true',
            help='disable the toolbar with debug on.')

    parser.add_argument(
            '--live-reload',
            action='store_true',
            help='Run with livereload server.'
            )

    args = parser.parse_args()

    # Now setup and run the application
    app = create_app('contrivers-cli-runner', debug=args.debug, testing=args.testing)

    # Disable the Debug toolbar with a flag
    if not args.no_bar:
        setupToolbar(app, args.testing)

    host, port = args.host.split(':')
    port = int(port)
    if args.live_reload:
        server = Server(app.wsgi_app)
        server.watch('app/')
        server.serve(host=host, port=port)
    else:
        app.run(use_reloader=args.no_reload, host=host, port=port)

