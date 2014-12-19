#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.utils
    ---------

"""
import codecs
import requests
from boto.s3.connection import S3Connection
# from .ext import cache


def ropen(url):
    """
    Open a file using requests.get

    :param url: the path to the file
    """
    resp = requests.get(url)
    return resp.text


def uopen(path):
    """
    Open a file using the python 2 codec library

    :param path: the path to the file.
    """
    with codecs.open(path, mode='r', encoding='utf-8') as f:
        return f.read()


# @cache.memoize()
def aopen(key_name, bucket_name='contrivers-assets'):
    """
    Return the contents of a S3 key object
    """
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)
    key_obj = bucket.get_key(key_name)
    contents = key_obj.get_contents_as_string()
    try:
        return contents.decode('utf-8')
    except UnicodeDecodeError:
        return contents


def asave(key_name, key_string, bucket_name='contrivers-assets'):
    """
    Save string to a S3 key object
    """
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    key.set_contents_from_string(key_string)


def aremove(key_name, bucket_name='contrivers-assets'):
    """
    Remove a S3 key from a bucket
    """
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)
    bucket.delete_key(key_name)


