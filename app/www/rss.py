#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.www.rss
    -----------

    Classes for generating RSS and Atom feeds.
"""

import datetime
from feedgen.feed import FeedGenerator
from urlparse import urljoin

from flask import url_for


class BaseFeedGenerator(object):
    """
    Class to encapsulate an Base Feed generator, the idea was to subclass
    this for RSS and Atom feeds, but feedgen has a bug that prevents atom feeds
    right now.

    """

    def __init__(self, root_url,
            query, title=u"Contrivers' Review",
            description=u"Main site feed"):
        self.root_url = root_url # request.url
        self.title = title
        self.description = description
        self.query = query  # should be iterable
        self.fg = self.create_generator()

    def __call__(self, query=None):
        if query is None:
            query = self.query
            self.create_entries()

    def create_generator(self):
        """ Setup and return a feedgen generator object """
        fg = FeedGenerator()
        fg.title(self.title)
        fg.id(self.root_url)
        fg.link(href=self.root_url, rel='alternate')
        fg.language(u'en')
        fg.description(self.description)
        fg.rights(u"Copyright Contrivers' Review {}".format(datetime.datetime.now().year))
        return fg

    def create_entries(self):
        raise NotImplementedError


class RssGenerator(BaseFeedGenerator):
    """SubClass of `BaseFeedGenerator` for RSS feeds"""

    def rss_file(self, *args, **kwargs):
        self.create_entries()
        return self.fg.rss_file(*args, **kwargs)

    def rss_str(self, *args, **kwargs):
        self.create_entries()
        return self.fg.rss_str(*args, **kwargs)

    def create_entries(self):
        fg = self.fg
        # fg.__dict__.__feed_entries = []
        for elem in self.query:

            # make the url that points to the web site
            canonical_url = urljoin(self.root_url, elem.make_url())

            # create a new entry object
            fe = fg.add_entry()

            fe.id(id=canonical_url) # permanent uri
            fe.title(title=elem.title)
            fe.updated(updated=elem.last_edited_date)
            fe.pubdate(elem.publish_date)

            # Atom 1.0 and Rss 2.0 don't support multiple authors
            # but neither is there a consensus on how to deal with
            # that omission.
            fe.author([{
                    'name': author.name,
                    'uri': url_for('frontend.authors', author_id=author.id),
                    'email': author.email
                    } for author in elem.authors ])

            fe.content(content=elem.html, type='html')
            fe.link(href=canonical_url, rel='alternate', title=elem.title)
            fe.description(description=elem.abstract, isSummary=True)
            for tag in elem.tags:
                fe.category(label=tag.tag, term=tag.tag)


