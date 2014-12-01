#-*- coding: utf-8 -*-
"""
    app.www.errors
    --------------

    App WWW errors. Raise errors with interesting information.
"""

from werkzeug.exceptions import HTTPException

class ApplicationError(Exception):
    pass


class FeatureComingSoon(HTTPException):
    code = 404
    name = "Page Not Found"
    description =\
        "<p>Our web site should still be considered beta software.</p>\n" + \
        "<p>You have requested a page that we have not yet implemented, " + \
        "but that we intend to add as soon as possible.</p>"

    def get_response(self, environment):
        resp = super(FeatureComingSoon, self).get_response(environment)
        resp.status = "%s %s" % (self.code, self.name.upper())
        return resp


class ArticleNotFound(HTTPException):
    code = 404
    name = "Article Not Found"
    description = \
        "You have requested an article that either does not exist, or " +\
        "existed previous but we removed it.  If you have questions, you can " +\
        "find our email on our Masthead."

