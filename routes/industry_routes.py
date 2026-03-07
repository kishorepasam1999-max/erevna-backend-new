# routes/title_namespace.py

from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.industry import Industry

api = Namespace("Industry", description="Manage Industry List")

# Swagger model
industry_model = api.model("Industry", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String(readonly=True),
    "name": fields.String(required=True, description="Title name")
})
@api.route("")
class IndustryList(Resource):

    @api.marshal_list_with(industry_model)
    def get(self):
        """Get all available industries"""
        industries = Industry.query.all()
        return industries
    @api.expect(industry_model)
    @api.marshal_with(industry_model, code=201)
    def post(self):
        """Add a new industry"""
        data = request.json
        name = data.get("name").strip()

        # Check if exists
        if Industry.query.filter_by(name=name).first():
            return {"message": "Industry already exists"}, 400

        new_industry = Industry(name=name)
        db.session.add(new_industry)
        db.session.commit()

        return new_industry, 201
