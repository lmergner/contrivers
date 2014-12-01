#/usr/bin/env python
#-*- coding: utf-8 -*-




def _slugify(text, delim=u'-'):
    """
    Generates an ASCII-only slug.

    http://flask.pocoo.org/snippets/5/
    """
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

    result = []
    for word in _punct_re.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))