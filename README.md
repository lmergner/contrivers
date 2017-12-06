# Contrivers' Review

[![Build Status](https://travis-ci.org/lmergner/contrivers.svg?branch=master)](https://travis-ci.org/lmergner/contrivers)

[Contrivers' Review](http://www.contrivers.org)

## Develop

1. Prereqs
    ```sh
    brew install python3 postgresql heroku
    python3 -m pip install virtualenvwrapper
    git clone https://github.com/contrivers-publishing/contrivers1.0
    mkvirtualenv -a <venv> -r requirements.txt -r test-requirements.txt <venv name>
    ```

2. Setup PostgreSQL

    You can [copy the production
    database](https://devcenter.heroku.com/articles/heroku-postgresql#pg-pull)
    or create a new local database.


    or by initializing it via flask-sqlalchemy:
    ```sh
    createdb contrivers
    ```

    then run some python code
    ```python
    from contrivers import create_app, db

    app = create_app(extra_config_vars={'SQLALCHEMY_DATABASE_URI'=<uri>})

    with app.test_request_context():
      db.create_all()
    ```

3. Start a dev server
    ```sh
    python run.py --help
    python run.py --testing --debug
    ```
    In your browser, open the `http://localhost:8000`

    if you have heroku installed, you can also test the app by running...
    ```sh
    heroku local web
    ```

## Deploying

## Testing

