#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    contrivers.utils
    ---------
"""
import codecs
from urllib import urlencode
from boto.s3.connection import S3Connection


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


