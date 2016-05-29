# -*- coding: utf-8 -*-
"""
    tests.test_ordered_queries

    Some queries should return a list ordered by
    the count of their relationships
"""

import pytest

@pytest.fixture
def order(db, data):
    authors = [x for x in data.authors(3)]
    articles = []
    articles.extend(self.defaults.articles(5, self.authors[0]))
    articles.extend(self.defaults.articles(3, self.authors[1]))
    articles.extend(self.defaults.articles(1, self.authors[2]))

    # Expect
    # author 1 has 5 articles
    # author 2 has 3 articles
    # author 3 has 1 article

    db.session.add_all(articles)
    db.session.commit()

