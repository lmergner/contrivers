#-*- coding: utf-8 -*-
"""
    contrivers.www.jinja_helpers
    ---------------------

    Main views jinja functions and filters

"""

import markdown

from . import www

def markdown_factory(extensions=None):
    """ return an initialized `markdown.Markdown` object

    Use an factory pattern to create a new markdown parser per request or
    unit of work. If you try to reuse a converter, it spits out cached
    results and that is not what we want.
    :params extensions: a list of extension names as strings to be loaded
        into the markdown converter. Defaults to footnotes, headerid, smarty
        and toc
    :returns: a Markdown object
    """

    if extensions is None:
        extensions = ['footnotes', 'headerid', 'smarty', 'tables']
    return markdown.Markdown(extensions=extensions)


@www.app_template_filter()
def md(txt):
    """Markdown Jinja2 template filter"""
    md = markdown_factory()
    return md.convert(txt)

@www.app_template_test()
def empty(ls):
    # TODO: give this a better name
    iter(ls)
    return True if len(ls) > 0 else False

