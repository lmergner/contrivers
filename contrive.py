#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
contrive

A tool to manage the process from markdown to the database.
"""

import sys
import os
import tempfile
import subprocess
import json
import six
from datetime import datetime

try:
    import click
except ImportError:
    print('Cannot import the Click library, is it installed?')
    print('$ workon <venv> && pip install -U click')
    exit(1)

def error(msg):
    click.echo(click.style('==> ', fg='red', bold=True) + msg)

def info(msg):
    click.echo(click.style('==> ', fg='green', bold=True) + msg)

try:
    import sqlalchemy
    from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
except ImportError:
    raise click.ClickException('Could not import sqlalchemy errors')


try:
    import yaml
except ImportError:
    raise click.ClickException('Cannot import yaml, have you installed PyYAML?')

try:
    from app import create_app, db
    from app.core import models
    from app.www.utils import uopen
except ImportError:
    error('Cannot import the contrivers python app, did you checkout the' +\
          'correct branch?')
    error('$ workon <venv> && git checkout master')
    raise click.ClickException('Cannot import contrivers lib')


DEFAULTS = dict(
    url='postgresql://contrivers@localhost/contrivers',
    excluded = ['tsvector', 'create_date'],
)


def get_heroku_url(app='contrivers', dbname='DATABASE_URL'):
    """ Shell out to the heroku cli tool to get the pg url """
    try:
        cmd = ['heroku', 'pg:credentials', dbname, '--app', app]
        output = subprocess.check_output(cmd).strip().split('\n')
        heroku_url = output[-1].strip()
    except subprocess.CalledProcessError:
        raise click.ClickException('Something went wrong getting the db url from heroku')
    return heroku_url


def edit_as_tmp(obj, prop):
    """ open the db version as a tempfile """
    #
    # Note: modifies the obj in place.
    #
    with tempfile.NamedTemporaryFile(suffix='.md') as tmp:
        tmp.write(getattr(obj, prop).encode('utf-8'))
        tmp.flush()
        subprocess.call(['$EDITOR', tmp.name])
        with open(tmp.name, 'r') as f:
            setattr(obj, prop, f.read())


def parse_yaml(f):
    """ Parse the yaml header out of a file """
    pointer = f.tell()
    if f.readline() != '---\n':
        f.seek(pointer)
        return ''
    readline = iter(f.readline, '')
    readline = iter(readline.next, '---\n')
    return ''.join(readline)


def jprint(obj):
    """ Pretty print a dictionary """
    print(json.dumps(
        obj, sort_keys=True, indent=4,
        separators=(',', ': ')))


def exists(model, attr, value):
    """ Check if it exists in the database """
    try:
        res = model.query.filter(attr == value).one()
        return res
    except:
        raise


@click.pass_obj
def process_headers(obj, headers, confirm=True):
    """ Parse the headers and replace collections with sqla objects """

    update = headers.copy()
    info('Title: ' + headers.get('title'))

    if confirm:
        update['type'] = click.prompt(
            'Please confirm or update the type'.format(**headers),
            default=headers.get('type'),
            )
    else:
        update['type'] = headers.get('type', 'article')

    #
    # Pop and Update Authors collection
    #
    authors = headers.pop('authors', [])
    if not authors:
        error('Hey, you need to specific a list of authors in the writing metadata.')
        sys.exit(1)
    update['authors'] = []
    for author in authors:
        if isinstance(author, int):
            # Get an existing author from db
            with app.test_request_context():
                update['authors'].append(models.Author.query.get(author))
        else:
            try:
                with obj.get('app').test_request_context():
                    au = models.Author.query.filter_by(email=author.get('email')).one()
                info('Using existing author {}'.format(au))
                update['authors'].append(au)
            except sqlalchemy.orm.exc.NoResultFound:
                update['authors'].append(models.Author(**author))

    if confirm:
        info("Authors: {}".format(update.get('authors', 'No authors found')))
        if not click.confirm('Is this correct?', default=True):
            sys.exit(1)

    #
    # Pop and Update Tags collection
    #
    tags = headers.pop('tags', [])
    if not tags \
       and confirm \
       and not click.confirm('Continue without tags or categories?'):
       sys.exit(1)
    update['tags'] = []
    for tag in tags:
        if isinstance(tag, int):
            # Get an existing tag from db
            with ctx.app.test_request_context():
                update['tags'].append(models.Tag.query.get(tag))
        else:
            try:
                with obj.get('app').test_request_context():
                    tg = models.Tag.query.filter_by(tag=tag).one()
                info('Using existing tag {}'.format(tg))
                update['tags'].append(tg)
            except sqlalchemy.orm.exc.NoResultFound:
                update['tags'].append(models.Tag(tag=tag))
    if confirm:
        info('Tags: {}'.format(update.get('tags', 'No Tags found.')))
        if not click.confirm('Is this correct?', default=True):
            sys.exit(1)

    #
    # Responses
    #
    responses = headers.pop('responses', [])
    headers['responses'] = []
    if responses:
        for response in responses:
            if not isinstance(response, int):
                error('Responses must be recorded by their id')
        error('We don\'t yet support adding a response')

    #
    # Books
    #
    if headers.get('type') == 'review':
        books = headers.get('book_reviewed')
        update['book_reviewed'] = []
        for book in books:
            book['isbn_10'] = unicode(book.get('isbn_10'))
            book['isbn_13'] = unicode(book.get('isbn_13'))
            if isinstance(book, int):
                update['book_reviewed'].append(models.Book.query.get(book))
            else:
                try:
                    with obj.get('app').test_request_context():
                        bk = models.Book.query.filter_by(isbn_13=book.get('isbn_13')).one()
                    info('Using existing book {}'.format(bk))
                    update['book_reviewed'].append(bk)
                except sqlalchemy.orm.exc.NoResultFound:
                    update['book_reviewed'].append(models.Book(**book))
        if confirm:
            info('Reviewed: {}'.format(update.get('book_reviewed', 'No books found.')))
            if not click.confirm('Is this correct?', default=True):
                sys.exit(1)

    if confirm:
        # Should be featured
        update['hidden'] = click.confirm(
                'Is the {} hidden?'.format(headers.get('type')),
                default=headers.get('hidden', False))
        # Should be hidden
        update['featured'] = click.confirm(
            'Is the {} featured?'.format(headers.get('type')),
            default=headers.get('featured', False))
    else:
        update['hidden'] = headers.get('hidden', False)
        update['featured'] = headers.get('featured', False)


    if not confirm:
        update['publish_date'] = datetime.utcnow()
    else:
        date = click.prompt('Enter the date to publish MM/DD/YYYY:', default=datetime.now().strftime('%m/%d/%Y'))
        update['publish_date'] = datetime.strptime(date, '%m/%d/%Y')

    return update

@click.group()
@click.option('-t', '--testing', is_flag=True, default=False, help='Use the local database')
@click.pass_obj
def cli(obj, testing):
    if testing:
        url = DEFAULTS.get('url')
    else:
        url = get_heroku_url()
    info('Using database at %s' % url)

    #
    # Make an app, because Flask...
    #
    app = create_app(
        additional_config_vars = { 'SQLALCHEMY_DATABASE_URI': url }
    )
    db = app.extensions.get('sqlalchemy').db

    obj['url'] = url
    obj['app'] = app
    obj['db'] = db


@cli.command()
@click.argument('filename', type=click.File('rb'))
@click.option('--confirm/--no-confirm', default=True, help='Do not prompt for confirmation')
@click.pass_obj
def add(obj, filename, confirm):

    # Pull out the yaml header info
    headers = yaml.load(parse_yaml(filename))
    text = filename.read()

    try:
        Model = getattr(models, headers.get('type').capitalize())
    except AttributeError:
        error('Cannot map the type to a model. Are you sure that it is right?')

    # Sanity check for duplicate titles
    with obj.get('app').test_request_context():
        try:
            exists = Model.query.filter_by(title=headers.get('title')).one()
            error('Existing title found in database: {}'.format(exists.id))
            sys.exit(1)
        except sqlalchemy.orm.exc.NoResultFound:
            pass

    headers = process_headers(
        headers,
        confirm=confirm,
        )

    # Add the writing by type
    writing = Model(**headers)
    writing.text = text

    with obj.get('app').test_request_context():
        obj.get('db').session.add(writing)
        obj.get('db').session.commit()


@cli.command()
@click.argument('_id', type=int)
@click.argument('filename', type=click.File('rb'))
@click.option(
    '-y', '--yes',
    is_flag=True,
    default=True,
    help='Do not prompt for confirmation')
@click.pass_obj
def update(obj, _id, filename, yes):
    """ Update an existing record """

    with obj.get('app').test_request_context():
        existing = models.Writing.query.get(_id)

    if not existing:
        error('No existing id found.')
        sys.exit(1)

    # Pull out the yaml header info and update from file
    headers = process_headers(
        yaml.load(parse_yaml(filename)),
        confirm=yes,
        )
    headers['text'] = filename.read()

    with obj.get('app').test_request_context():
        for key in headers.keys():
            if not key in sqlalchemy.inspect(existing).attrs:
                error('Cannot find key {}. Skipping...'.format(key))
                continue
            info('Updating {}'.format(key))
            setattr(existing, key, headers.get(key))
        obj.get('db').session.add(existing)
        obj.get('db').session.commit()

@cli.group(chain=True)
def ls():
    pass

@ls.command('authors')
@click.pass_obj
def authors(obj):
    with obj.get('app').test_request_context():
        authors = models.Author.query.order_by('id').all()


    info('Authors')

    width = 0
    for author in authors:
        if len(author.name) > width:
            width = len(author.name)

    cols = '{id:<4} {name:<{width}} {email}'

    click.echo(click.style(cols.format(
        id='ID', name='Name', email='Email', width=width), bold=True))
    for author in authors:
        click.echo(cols.format(
            id=author.id,
            name=author.name.encode('ascii', 'ignore'),
            email=author.email.encode('ascii', 'ignore'),
            width=width,
            ))


def print_writings(writings):
    cols = '{id:4} {type:10} {title:<{width}}'

    width = 0
    for ess in writings:
        if len(ess.title) > width:
            width = len(ess.title)

    click.echo(click.style(cols.format(
            id='ID',
            type='Type',
            title='Title',
            width=width,
        ),
        bold=True))

    for ess in sorted(writings, key=lambda x: x.id):
        click.echo(cols.format(
            id=ess.id,
            type=ess.type,
            title=ess.title,
            width=width,
            ))


@ls.command('reviews')
@click.pass_obj
def reviews(obj):
    with obj.get('app').test_request_context():
        writings = models.Review.query.order_by('id').all()
    info('Reviews')
    print_writings(writings)


@ls.command('articles')
@click.pass_obj
def articles(obj):
    with obj.get('app').test_request_context():
        writings = models.Article.query.order_by('id').all()
    info('Articles')
    print_writings(writings)


@ls.command('books')
@click.pass_obj
def books(obj):
    with obj.get('app').test_request_context():
        books = models.Book.query.order_by('id').all()
    info('Books')
    for book in books:
        click.echo('{id:4} {title}'.format(
            id=book.id,
            title=book.title))


@cli.command()
@click.pass_obj
@click.argument('ids', nargs=-1)
@click.option('--confirm/--no-confirm', default=True, help='Do not prompt for confirmation')
def rm(obj, ids, confirm):
    info('Deleting ' + ' '.join(ids))
    with obj.get('app').test_request_context():
        for _id in ids:
            target = models.Writing.query.get(_id)
            if not target:
                error('Id {} not found'.format(_id))
                continue
            click.echo(click.style('==> ', fg='yellow') + '{id} {title}'.format(
                id=target.id,
                type=target.type,
                title=target.title,
                ))

            if not confirm or click.confirm('Really delete?'):
                obj.get('db').session.delete(target)
        obj.get('db').session.commit()


@cli.command('info')
@click.pass_obj
@click.argument('ids', nargs=-1)
@click.option('--text/--no-text', default=False)
@click.option('--abstract/--no-abstract', default=False)
def display_info(obj, ids, text, abstract):

    info('Info ' + ' '.join(ids))
    with obj.get('app').test_request_context():
        for _id in ids:
            target = models.Writing.query.get(_id)
            if not target:
                error('ID {} not found'.format(_id))
                continue

            for prop in sqlalchemy.inspect(target).attrs:
                if prop.key in DEFAULTS.get('excluded'):
                    continue
                elif prop.key.startswith('_'):
                    continue
                elif prop.key == 'text' or prop.key == 'abstract':
                    continue
                elif isinstance(prop.value, six.string_types):
                    val = prop.value
                elif isinstance(prop.value, datetime):
                    val = prop.value.strftime('%m/%d/%Y')
                else:
                    val = prop.value
                click.echo(click.style(prop.key, bold=True), nl=False)
                click.echo(' ', nl=False)
                click.echo(val)

            if text:
                click.edit(text=target.text)
                click.echo('Please note that no changes were saved. To edit, please use the <update> command.')

            if abstract:
                click.edit(text=target.abstract)
                click.echo('Please note that no changes were saved. To edit, please use the <update> command.')


@cli.group()
@click.argument('_id', type=int)
@click.pass_obj
def author(obj, _id):
    with obj.get('app').test_request_context():
        obj['author'] = models.Author.query.get(_id)

@author.command('edit')
@click.argument('column', type=str)
@click.pass_obj
def edit_author(obj, column):
    author = obj.get('author')
    if column == 'bio':
        res = click.edit(author.bio)
        if res:
            author.bio = res
    else:
        error('Only edit bios right now')
    with obj.get('app').test_request_context():
        obj.get('db').session.add(author)
        obj.get('db').session.commit()


if __name__ == '__main__':
    cli(obj={})
