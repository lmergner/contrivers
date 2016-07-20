# -*- coding: utf-8 -*-
# pytest: disable=no-member

import pytest
from contrivers.models import Article, Review, Author

def test_article_url(data):
    article = data.article()
    assert article.url() == 'http://localhost/articles/'
    article.slug = '-'.join(article.title.lower().split())
    data.add_and_commit(article)
    article = Article.query.first()
    assert article.url() == 'http://localhost/articles/1/test-article/'


def test_review_url(data):
    review = data.review()
    assert review.url() == 'http://localhost/reviews/'
    review.slug = '-'.join(review.title.lower().split())
    data.add_and_commit(review)
    review = Review.query.first()
    assert review.url() == 'http://localhost/reviews/1/test-review/'

def test_author_url(data):
    author = data.author()
    assert author.url() == 'http://localhost/authors/'
    data.add_and_commit(author)
    author = Author.query.first()
    assert author.url() == 'http://localhost/authors/1/luke-thomas-mergner/'
