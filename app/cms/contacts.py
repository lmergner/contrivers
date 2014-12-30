#/usr/bin/env python
#-*- coding: utf-8 -*-

import json
from flask import Blueprint, render_template, Response, jsonify, Flask, current_app, request
from flask.views import MethodView
from sqlalchemy import Integer, String, DateTime, Column

from .ext import db


def make_success():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def make_list_response(iterable_obj):
    return Response(json.dumps(iterable_obj), mimetype='application/json')


class ContactsAPI(MethodView):

    def get(self, contact_id):
        if contact_id is None:
            return make_list_response([obj.serialize for obj in  q(Contact).all()])
        else:
            return jsonify(q(Contact).get(contact_id).serialize)

    def post(self):
        new_contact = Contact(**request.json)
        db.session.add(new_contact)
        db.session.commit()
        return make_success()

    def delete(self, contact_id):
        db.session.delete(db.session.query(Contact).get(contact_id))
        return make_success()

    def put(self, contact_id):
        contact = q(Contact).get(contact_id)
        for key in request.json:
            contact[key] = request.json[key]
        db.session.commit()
        return make_success()

contact_view = ContactsAPI.as_view('contacts_api')
contact_manager.add_url_rule('/contacts/', defaults={'contact_id': None},
                         view_func=contact_view, methods=['GET',])
contact_manager.add_url_rule('/contacts/', view_func=contact_view, methods=['POST',])
contact_manager.add_url_rule('/contacts/<int:contact_id>', view_func=contact_view,
                         methods=['GET', 'PUT', 'DELETE'])

def init_db():
    with current_app.test_request_context():
        db.create_all()
        test_data = {
            'Luke': 'lmergner@gmail.com',
            'Pete': 'psinnott@gmail.com',
            'Gregory Kenneth Mergner': 'greg.mergner@gmail.com',
            'Volker Smith': 'dummy@example.com',
            'Slavoj Zizek': 'prolix@lacan.com'}
        for entry in test_data:
            try:
                db.session.query(Contact).filter_by(name=entry).one()
            except:
                contact = Contact(name=entry, email=test_data[entry])
                db.session.add(contact)
            else:
                pass
        db.session.commit()


if __name__ == '__main__':
    app = Flask('contacts-app')
    app.debug = True

    @app.context_processor
    def inject_variables():
        class DummyVars(object):
            def __init__(self, **kwargs):
                for key in kwargs:
                    setattr(self, key, kwargs[key])
        return {'site': DummyVars(title=u"Contrivers' Review"),
                'login': DummyVars(username=u'Luke Thomas Mergner')}

    app.register_blueprint(contact_manager)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db.init_app(app)
    init_db(app)

    @app.route('/')
    def index():
        render_template('contacts.html')

    app.run(host='0.0.0.0', port=8001)



