# Contrivers' Review 

Hi! Welcome to the rube goldberg of web sites.

[![Build Status](https://travis-ci.org/lmergner/contrivers.svg?branch=master)](https://travis-ci.org/lmergner/contrivers)

The web technologies behind [Contrivers' Review](http://www.contrivers.org) are
divided into several different repositories.

1. A [Python html server app](http://www.github.com/lmergner/contrivers) that
   generates the www site.
2. A [Node API server](http://www.github.com/lmergner/contrives-api) that allows CRUD operations.
3. A [React CMS app](http://www.github.com/lmergner/contrivers-cms) that allows
   secure administration of the database.
4. [Stylesheets](http://www.github.com/lmergner/contrivers-styles)
5. A [set of migration
   scripts](http://www.github.com/lmergner/contrivers-migrations) for the
   database, written in bash, sql, and python's [alembic][] library.

The apps and database are currently hosted on (www.heroku.com). The stylesheets will be hosted on Amazon S3.

[alembic]: http://alembic.zzzcomputing.com/en/latest/

## Design

The main web site is built on the [Flask][]. It is a server-side rendering app:
meaning that a dynamic html page is created by the server and sent to the
client, rather than javascript creating a page from data in the browser.
`Flask` is more friendly to micro-service architectural patterns, where instead
of a monolithic app performing many jobs each task has a dedicated process that
can be scaled independently. That said, Flask is more than a library. It is a
framework with certain obligations. Notably, Flask is designed to use
"contexts." An `app` context is created at runtime for each app and a `request`
context is created for each request. Both contexts are kept on a stack by the
runtime. You won't need to worry about the contexts directly, and this is one
area where using Flask incurs a complexity penalty that we don't need. However,
there is code that must be context-ware: for example, using the
`flask.current_app` or `app.test_request_context`. Contexts are explained a bit
[in this talk][armin] from framework author Armin Ronacher.

Flask also tries to help us build modular apps with the idea of [Blueprints]
and [Extensions]. The first are views, in Django parlance, but can be
dynamically added at runtime, as contrivers tries to do in the
`__init__.create_app` function.  The latter are prepackaged libraries that add
functionality at runtime, such as [flask-admin][]. These must be configured,
but differ from Blueprints, which must be built up by the app author.

As a server-side app, `contrivers` mostly builds html pages out of [jinja][]
templates. Flask is designed to use Jinja without any modification. Templates
are kept in `./templates`. (If you want to use Jinja in javascript, check out
Mozilla's [nunjucks][] library.) You may want to read about template
inheritance first in the jinja docs. `templates/layout.html` is the base or parent
template for contrivers.

`contrivers` is moving towards a micro-service pattern by separating the renderer,
stylesheets, migration scripts, and CMS / API. Functionally, each piece should
strive to be ignorant of "state." State or "config" should be represented by a
PostgreSQL database or similar datastore, not in a configuration file (pace
Django). At least, that's the goal though you'll see some configuration scattered
in some py files (config.py or cfg.py) and in templates. 

The database schema is defined in [sqlalchemy][], which is a python ORM. See
`app/core/models.py` in master or `contrivers/models.py` in develop.  It is the
best python ORM. Postgres is relational, and SQLA handles all the joins and
automatically turns queries into objects. Even complex relationships like
[adjacency][] or self-referencial lists are handled for us. However, it also
locks us into both sqlalchemy (if we can't rewrite the queries in SQL) and it
locks us into using the "declarative" extension to sqlalchemy, which isn't
compatible with some other design patterns. To use sqlalchemy with Flask, we
use the flask-sqlalchemy extension, which has a few customizations. This means
we can't use the model.py without creating a Flask app with an app context.
This is dumb and means it sucks to write simple db scripts. If there is
technical debt in the code, it's here in the decision to use sqlalchemy,
adjacency tables, and flask together.

The master branch supports python 2.7; the develop branch is moving
towards support for python 3.5 in order to take advantage of the `asyncio`
library and other stuff.

[Flask]: https://github.com/pallets/flask  
[Jinja]: https://github.com/pallets/jinja
[armin]: http://pyvideo.org/europython-2012/advanced-flask-patterns.html
[blueprints]: http://flask.pocoo.org/docs/0.11/blueprints/
[extensions]: http://flask.pocoo.org/docs/0.11/extensions/
[flask-admin]: http://flask-admin.readthedocs.io/en/latest/
[nunjucks]: https://mozilla.github.io/nunjucks/
[sqlalchemy]: http://www.sqlalchemy.org/
[adjacency]: http://docs.sqlalchemy.org/en/latest/orm/self_referential.html

## Running Locally 

1. Python
  ```
  brew install python versions/postgres9.5 heroku
  pip install virtualenvwrapper
  ```

2. Git
  ```
  brew install git
  brew install git-flow-avh
  ```

3. Clone
  ```
  git clone https://github.com/lmergner/contrivers <dest>
  git checkout <branch>
  ```

4. Create a virtualenv 
  `mkvirtualenv -a <venv> -r requirements.txt -r test-requirements.txt <venv name>`

  Unlike NPM, Python doesn't isolate current working directory by default.

5. Create a postgres database

  Usually I create a `contrivers` pg user. I'm thinking that in the future, I 
  can use pg schemas to isolate access to certain tables by user / app. However, 
  if you don't create a special user, then you'd use your Unix username as the 
  default.
 
  If you have access to heroku, you can copy the master or develop database...

  ```
  heroku pg:pull DATABASE_URL postgres://<username>@localhost/contrivers[-develop] --app contrivers[-develop]
  ```

  If you don't have access to a copy of the database, you can build an empty
  database using the contrivers-migration repo, or by running a pythong script...

  Note:  In the develop branch, `app` is renamed to `contrivers`.
  ```
  from app import create_app, db

  app = create_app(extra_config_vars={'SQLALCHEMY_DATABASE_URI'=<uri>})

  with app.test_request_context():
      db.create_all()
  ```

6. Start a dev server
  ```
  git checkout master
  python run.py --help
  python run.py --testing --debug
  ```
  In your browser, open the `http://localhost:8000`

## CI server

On every push to master or develop, [travis-ci][] is supposed to run all the tests. 

Note: It never deploys the master branch to production. That is currently done with
the heroku cli or web interface.

[travis-ci]: https://travis-ci.org/lmergner/contrivers

## Server

The website is deployed on [heroku][]. You downloaded the cli client in step 1.
If you are a collaborator, you can be added to the heroku team.  
  ```
  heroku --help
  heroku login
  heroku apps
  ```

Heroku [Pipelines][] allow different commits or revisions from a repo
to be deployed as an app. Of particular interest is the concept of a 
"Review App".

Currently, there are three apps.

  1. contrivers (production):  an untagged push from the master branch. Actually, because I
     did a lot of history editing, this commit no longer matches anything in
     Github. I'm smart.
  2. contrivers-next: the bugfixes committed to master, ahead of production.  Next and
     production share a database, so don't mess with the data when using next.
  3. contrivers-develop: a branch representing future features and database schemas. It is
     backed by a separate database

[heroku]: https://www.heroku.com/
[pipelines]: https://devcenter.heroku.com/articles/pipelines

## Testing

All changes should have unittests. I'd like to also have integration tests
using something like [casperjs][].

Note:  only develop currently passes all tests.

Note:  master branch uses the builtin `unittest` library; the develop branch
uses [pytest][].

[pytest]: http://pytest.org/
[casperjs]: http://casperjs.org/

  `make test`
  - or - 
  `py.test`
  - or - 
  `python -m unittest discover -s tests`

## Adding new articles

I have a separate virtualenv for the master branch called `hotfix`. But regardless, the
requirements are different between the branches.

In master, there's an admin extension (http://localhost:8000/admin). It's buggy.

There may also be a `./contrive.py` file that reads a [Jekyll file with
frontmatter][jekyll] to add a new writing. It may also update, delete, or list rows from
the database.

[jekyll]: http://jekyllrb.com/docs/frontmatter/

## Contributing

Note: Work in Progress

- open/close issues
- branch and write code
- write tests (!!!)
- create a pull request (??) or heroku pipeline app
- copyedit the docs

## Major Planned Features

Note: any style changes should be made in the styleguides repo. The python repo
is defines the HTML but is ignorant of how it is styled, except insofar as it
must embed a link in the `templates/layout.html`.

- Custom Markown Renderer (using [mistune][]?)
- proper caching with Redis
- Intro support as a Writing subclass
- Ebooks:  prebuilt or dynamically generated, but step one is writing the
  ebook-builder code, then the UI and caching.\
- Move from Google Analytics to in-house analytics and error notification

[mistune]: https://github.com/lepture/mistune

## Major Design Questions

- Migrations vs. Schema definition: should we combine migrations back into
   this repo or divorce the schema from the code. 
- Micro-Services: It's not a big or complicated app. Are even smaller apps
  appropriate to separate concerns?
- Python 3.5 Async Support: Experimental Branch using [Growler][] that lets
  us write Python apps that look like Node apps. The API app is written in 
  KoaJS, which Growler is similar to. This is a learning branch.

[growler]: https://github.com/pyGrowler/Growler
