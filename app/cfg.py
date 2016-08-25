#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.mutable_config
    ------------------

    Functions to load the config from an external file *per request*. We can
    then load new assets or other UI elements dynamically.

    Currently this is only a mock object representing an API for the app to
    plug in.

"""

class SiteConfig(object):
    """Pass to templates so we can use dot notation for lookups."""
    def __init__(self):
        self.title = u'Contrivers\' Review'
        self.tagline = u'Theory, Politics, Criticism'
        self.twitter_name = 'contriversrev'
        self.amzn_tag = 'contrivers-review-20'
        self.twitter_image = ''
        self.apple_touch_icons = []
        self.description =\
            u"Contrivers’ Review is a non-profit digital publication in " +\
            u"tradition of intellectual journals, publishing the best " +\
            u"essays on political and social theory."

        self.announcements = [
            ]
