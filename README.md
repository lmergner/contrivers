# Contrivers' Review

[![Build Status](https://travis-ci.org/lmergner/contrivers.svg?branch=master)](https://travis-ci.org/lmergner/contrivers)

[Contrivers' Review](http://www.contrivers.org)

## Develop

1. Python
  ```
  brew install python3 postgresql
  python3 -m pip install virtualenvwrapper
  ```

2. Git
  ```
  brew install git
  ```

3. Clone
  ```
  git clone https://github.com/contrivers-publishing/contrivers1.0
  ```

4. Create a virtualenv
  `mkvirtualenv -a <venv> -r requirements.txt -r test-requirements.txt <venv name>`


5. Create a postgres database

by cloning from heroku...
  ```
  heroku pg:pull DATABASE_URL postgres://<username>@localhost/contrivers-develop --app contrivers[-develop]
  ```
or by initializing it via flask-sqlalchemy:
  ```
  createdb contrivers-develop
  ```
the  `create.py` file:
  ```
  from app import create_app, db

  app = create_app(extra_config_vars={'SQLALCHEMY_DATABASE_URI'=<uri>})

  with app.test_request_context():
      db.create_all()
  ```

6. Start a dev server
  ```
  python run.py --help
  python run.py --testing --debug
  ```
  In your browser, open the `http://localhost:8000`

if you have heroku installed, you can also test the app by running...
  ```
  heroku local web
  ```

## Deploying

## Testing

