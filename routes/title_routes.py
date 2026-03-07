# routes/title_namespace.py

from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.title import Title

api = Namespace("Titles", description="Manage Title List (Mr, Mrs, Dr, etc.)")

# Swagger model
title_model = api.model("Title", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String(readonly=True),
    "name": fields.String(required=True, description="Title name")
})
@api.route("")
class TitleList(Resource):

    @api.marshal_list_with(title_model)
    def get(self):
        """Get all available titles"""
        titles = Title.query.all()
        return titles
    @api.expect(title_model)
    @api.marshal_with(title_model, code=201)
    def post(self):
        """Add a new title (e.g., Mr., Mrs., Dr.)"""
        data = request.json
        name = data.get("name").strip()

        # Check if exists
        if Title.query.filter_by(name=name).first():
            return {"message": "Title already exists"}, 400

        new_title = Title(name=name)
        db.session.add(new_title)
        db.session.commit()

        return new_title, 201
