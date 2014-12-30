#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    app.api.views
    -------------

    Endpoints for api
"""

from flask import json, jsonify, Response, request
from flask.views import MethodView
from ..core.ext import db

q = db.session.query

def make_success():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def make_list_response(iterable_obj):
    return Response(json.dumps(iterable_obj), mimetype='application/json')

class ApiView(MethodView):
    """ Subclass of Flask's `MethodView` that takes a model on construction and
    performs CRUD operations using JSON """

    def __init__(self, model):
        super(ApiView, self).__init__()
        self.model = model

    def get(self, model_id):
        if model_id is None:
            return make_list_response([x.serialize for x in q(self.model).all()])
        else:
            return jsonify(q(self.model).get(model_id).serialize)

    def post(self):
        new_model = self.model(**request.json)
        db.session.add(new_model)
        db.session.commit()
        return make_success()

    def delete(self, model_id):
        db.session.delete(db.session.query(self.model).get(model_id))
        return make_success()

    def put(self, model_id):
        _model = q(self.model).get(model_id)
        for key in request.json:
            setattr(_model, key, request.json[key])
        db.session.commit()
        return make_success()

def api_view_factory(blueprint, models):
    for model in models:
        endpoint = '/' + model.__name__.lower() + 's/'
        model_view = ApiView.as_view(model.__name__.lower() + '_api', model)
        blueprint.add_url_rule(endpoint,
                defaults={'model_id': None},
                view_func=model_view, methods=['GET',])
        blueprint.add_url_rule(endpoint, view_func=model_view, methods=['POST',])
        blueprint.add_url_rule(endpoint + '<int:model_id>', view_func=model_view,
                                 methods=['GET', 'PUT', 'DELETE'])

