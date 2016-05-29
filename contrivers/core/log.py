#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.log
    -------

    Local logging config.

"""

import logging

def configure_logger(app):
    """Instantiate a few logger handlers and set the
    appropriate levels."""

    level = logging.DEBUG if app.debug else logging.WARNING
    app.logger.setLevel(level)
    del app.logger.handlers[:]

    # Log all errors at 'level' to the console
    # with colored error warnings
    col_handler = logging.StreamHandler()
    col_handler.setFormatter(ColorFormatter())
    col_handler.setLevel(level)
    app.logger.addHandler(col_handler)

    if not app.debug:
        # Log all error at 'level' to the database
        # db_handler = DBHandler()
        # db_handler.setLevel(level)
        # app.logger.addHandler(db_handler)

        # Log all errors at ERROR to email
        # Currently no way to change the address from this function
        mail_handler = GmailLogger(
            ('smtp.gmail.com', 587),
            'lmergner+contrivers@gmail.com',
            'lmergner@gmail.com',
            'Contrivers SERVER ERROR',
            credentials=('lmergner', 'hogjvlbescbtnimh'))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # configure sqlalchemy logger
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

