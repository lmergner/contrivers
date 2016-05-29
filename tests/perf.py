#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Rudimentary performance tests
"""

import argparse
import sys
import os
import time
import datetime
import json
import mock
import warnings
import inspect
import cProfile, pstats, StringIO
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from contrivers import create_app
from contrivers.core.models import Tag, Author

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    app = create_app(testing=True, debug=False, additional_config_vars={'SQLALCHEMY_ECHO': False})
DATABASE = 'postgresql://contrivers@localhost/contrivers'

class log(object):
    INFO = 1
    WARN = 2
    ERROR = 3
    m = {
        1: 'INFO',
        2: 'WARN',
        3: 'ERROR', }
    c = {
        1: '\033[92m',  # green
        2: '\033[93m',  # yellow
        3: '\033[91m',  # red
        4: '\033[97m',  # bold white, i think
        0: '\033[0m'}

    @classmethod
    def ts(cls):
        return '{}[{}]{}'.format(
            cls.c[4],
            datetime.datetime.now().strftime('%H:%M:%S'),
            cls.c[0])

    @classmethod
    def msg(cls, lvl, msg):
        return '{ts} {color}{lvl}{end} {msg}'.format(
            ts=cls.ts(),
            color=cls.c[lvl],
            lvl=cls.m[lvl],
            end=cls.c[0],
            msg=msg
        )

    @classmethod
    def warn(cls, msg):
        print(cls.msg(2, msg))

    @classmethod
    def error(cls, msg):
        print(cls.msg(3, msg))

    @classmethod
    def info(cls, msg):
        print cls.msg(1, msg)

    @classmethod
    def result(cls, test, result):
        print('{}{}{} {}'.format(cls.c[4], test, cls.c[0], result))


@contextmanager
def session_scope(maker):
    session = maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class timer(object):
    """ time functions and record results """
    results_file = os.path.abspath('tests/perf.json')
    run_time = datetime.datetime.utcnow().isoformat()
    results = {}
    tests = []
    times = 100
    groups = {}
    group_name = None

    def __init__(self, group=None, profile=False):
        if group:
            self.group_name = group
        self.profile = profile

    def __call__(self, wrapped):
        self.wrapped_func = wrapped
        self.__class__.tests.append(self.time(wrapped))
        if self.profile:
            self.__class__.tests.append(self.profile(wrapped))

        if self.group_name in self.__class__.groups:
            self.__class__.groups[self.group_name].append(self.wrapped_func.__name__)
        else:
            self.__class__.groups[self.group_name] = [self.wrapped_func.__name__]


    def time(self, wrapped):
        def wrapper(*args, **kwargs):
            local_timer = None
            for x in xrange(self.__class__.times):
                start = time.time()
                wrapped(*args, **kwargs)
                end = time.time()
                if local_timer == None:
                    local_timer = end - start
                else:
                    local_timer = self.average(local_timer, end - start)
            self.register(local_timer, '')

        return wrapper

    def profile(self, wrapped):
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            wrapped(*args, **kwargs)
            pr.disable()
            self.register(pr.print_stats(sort='time'), 'cProfile_')
        return wrapper

    @staticmethod
    def average(average, value):
        return (average + value) / 2.0

    @classmethod
    def read(cls):
        try:
            with open(cls.results_file) as j:
                return json.load(j)
        except (IOError, ValueError):
            return {}

    @classmethod
    def write(cls):
        existing = cls.read()
        existing.update({cls.run_time: cls.results})
        with open(cls.results_file, 'w') as j:
            json.dump(existing, j)

    def register(self, result, prefix):
        key = self.wrapped_func.__name__
        self.__class__.results[key] = result

    @classmethod
    def run(cls):
        for test in cls.tests:
            test()
        cls.write()

    @classmethod
    def compare(cls):
        results = cls.read()
        for group in cls.groups:
            print '*** ', group, ' ***'
            for run in results.keys():
                print '*** ', run, '***'
                for test in cls.groups[group]:
                    log.result(test, results[run][test])



@timer('tag')
def tag_count_in_python():
    with session_scope(Session) as sess:
        tags = sess.query(Tag).all()
        return sorted(tags, key=lambda x: x.count, reverse=True)

@timer('tag')
def tag_count_in_sqla():
    with session_scope(Session) as sess:
        return Tag.ordered_query()

@timer('author')
def author_count_in_python():
    with session_scope(Session) as sess:
        authors = sess.query(Author).all()
        return sorted(authors, key=lambda x: x.count, reverse=True)

@timer('author')
def author_count_in_sqla():
    with session_scope(Session) as sess:
        return Author.ordered_query()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', action='store_true')
    args = parser.parse_args()

    if args.clean:
        os.remove(timer.results_file)

    app.test_request_context().push()

    engine = create_engine(DATABASE, echo=False)
    Session = sessionmaker(bind=engine)

    timer.run()
    timer.compare()
