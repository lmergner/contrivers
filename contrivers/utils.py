#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    contrivers.utils
    ---------
"""
import logging
import codecs
from urllib import urlencode
import boto3
import botocore
from functools import update_wrapper
import datetime
from pytz import timezone
from ._compat import iteritems


def cache(fn):
    """ Simple in-memory memoizer for caching network calls """
    _cache = {}

    def build_key(name, args, kwargs):
        key = name + '::'
        key += '|'.join([str(arg) for arg in args])
        key += '+'.join(
            ['{}={}'.format(key, val) for key, val in iteritems(kwargs)]
        )
        return key

    def wrapper(*args, **kwargs):
        logging.debug('cache %s', _cache)
        key = build_key(fn.__name__, args, kwargs)
        if key in _cache:
            return _cache[key]
        else:
            res = fn(*args, **kwargs)
            _cache[key] = res
            return res

    update_wrapper(wrapper, fn)
    return wrapper


def uopen(path):
    """
    Open a file using the python 2 codec.

    :param path: the path to the file.
    """
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def clip_string(string, length):
    """
    Take a string, truncate it, and append an ellipsis.
    """
    if len(string) <= length:
        return string
    else:
        ellipsis = u"\u2026"
        ustring = string[0:length]
        return ustring


def instapaper_url(url, title, abstract):
    """
    Build in instapaper url.

    :params url:
    :params title:
    :params abstract:
    :returns string: an url that saves the article to instapaper serice

    check django docs for urlencode with unicode
    """
    base = 'http://www.instapaper.com/hello2?'
    params = {
        'url': url,
        'title': title,
        'abstract': clip_string(abstract, 99)}
    return base + urlencode(params)


@cache
def aopen(key_name, bucket_name='contrivers-assets'):
    """ Return the contents of a S3 key object """
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket_name, Key=key_name)
        contents = obj.get('Body').read()
        utf = contents.decode('utf-8')
        logging.debug('boto3 get_object decodes properly from utf-8')
        return utf
    except UnicodeDecodeError:
        logging.debug('boto3 get_object threw an error decoding from utf-8')
        return contents
    except botocore.exceptions.ClientError as err:
        # TODO: handle ClientError
        raise err


def asave(key_name, bucket_name='contrivers-assets'):
    """ Save string to a S3 key object """
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=key_name)
    except botocore.exceptions.ClientError as err:
        # TODO: handle ClientError
        raise err


def aremove(key_name, bucket_name='contrivers-assets'):
    """
    Remove a S3 key from a bucket
    """
    try:
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=bucket_name, Key=key_name)
    except botocore.exceptions.ClientError as err:
        # TODO: handle ClientError
        raise err

def has_timezone(dt):
    """ Return True if datetime object has a tzinfo attribute """
    if not isinstance(dt, datetime.datetime):
        raise TypeError('Expected a datetime object')
    if dt.tzinfo is not None:
       return True
    return False

def with_utc(dt):
    """ return a datetime with a UTC timezone

    If the datetime is non-UTC, it will be converted. If the datetime is
    naive, UTC will be added.
    """
    if not has_timezone(dt):
        return dt.replace(tzinfo=timezone('UTC'))
    else:
        return dt.astimezone(timezone('UTC'))
