from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.research_request import ResearchRequestNew
from datetime import datetime
from flask_cors import cross_origin



api = Namespace("ResearchRequests", description="Manage Research Requests")

# Swagger Model
request_model = api.model("ResearchRequestNew", {
    "uuid": fields.String,
    "client_uuid": fields.String,
    "client_name": fields.String,
    "contact_name": fields.String,
    "contact_email": fields.String,
    "contact_phone": fields.String,
    "title": fields.String,
    "description": fields.String,
    "research_objectives": fields.List(fields.String),
    "target_sample_size": fields.Integer,
    "target_demographics": fields.String,
    "preferred_locations": fields.List(fields.String),
    "timeline": fields.String,
    "budget_range": fields.String,
    "special_requirements": fields.String,
    "proposed_games": fields.List(fields.String),
    "status": fields.String,
    "submitted_at": fields.String,
    "priority": fields.String,
    "appointment_date": fields.String,
    "appointment_time": fields.String
})


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    # Try to parse with timezone first, then without
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        # If the string has a timezone, remove it
        if 'Z' in dt_str:
            return datetime.fromisoformat(dt_str.replace('Z', ''))
        elif '+' in dt_str:
            return datetime.fromisoformat(dt_str.split('+')[0])
    return None

# ---------------------------------------------------------
# CREATE REQUEST
# ---------------------------------------------------------
@api.route("/")
class CreateResearchRequest(Resource):

    # @api.expect(request_model)
    # def post(self):
    #     data = request.get_json()

    #     new_req = ResearchRequestNew(
    #         uuid=data.get("uuid"),
    #         client_uuid=data.get("client_uuid"),
    #         client_name=data.get("client_name"),
    #         contact_name=data.get("contact_name"),
    #         contact_email=data.get("contact_email"),
    #         contact_phone=data.get("contact_phone"),
    #         title=data.get("title"),
    #         description=data.get("description"),
    #         research_objectives=data.get("research_objectives"),
    #         target_sample_size=data.get("target_sample_size"),
    #         target_demographics=data.get("target_demographics"),
    #         preferred_locations=data.get("preferred_locations"),
    #         timeline=data.get("timeline"),
    #         budget_range=data.get("budget_range"),
    #         special_requirements=data.get("special_requirements"),
    #         proposed_games=data.get("proposed_games"),
    #         status=data.get("status"),
    #         # submitted_at=datetime.fromisoformat(data.get("submitted_at").replace("Z", "")),
    #         submitted_at = parse_iso_datetime(data.get("submitted_at")),
    #         priority=data.get("priority"),
    #         appointment_date=data.get("appointment_date"),
    #         appointment_time=data.get("appointment_time")
    #     )

    #     db.session.add(new_req)
    #     db.session.commit()

    #     return {"message": "Research request created successfully"}, 201

    @api.expect(request_model)
    def post(self):
        data = request.get_json()

        new_req = ResearchRequestNew(
            uuid=data.get("uuid"),
            client_uuid=data.get("client_uuid"),
            client_name=data.get("client_name"),
            contact_name=data.get("contact_name"),
            contact_email=data.get("contact_email"),
            contact_phone=data.get("contact_phone"),
            title=data.get("title"),
            description=data.get("description"),

            # JSON fields MUST be lists or dicts
            research_objectives=data.get("research_objectives") or [],
            target_sample_size=data.get("target_sample_size"),
            target_demographics=data.get("target_demographics"),
            preferred_locations=data.get("preferred_locations") or [],
            timeline=data.get("timeline"),
            budget_range=data.get("budget_range"),
            special_requirements=data.get("special_requirements"),
            proposed_games=data.get("proposed_games") or [],

            status=data.get("status"),
            submitted_at=parse_iso_datetime(data.get("submitted_at")),
            priority=data.get("priority"),

            # NEW FIELDS
            appointment_date=data.get("appointment_date"),
            appointment_time=data.get("appointment_time"),
        )

        db.session.add(new_req)
        db.session.commit()

        return {"message": "Research request created successfully"}, 201


# ---------------------------------------------------------
# GET SINGLE REQUEST
# ---------------------------------------------------------
@api.route("/<string:uuid>")
class ResearchRequestByUUID(Resource):
    def get(self, uuid):
        req = ResearchRequestNew.query.filter_by(uuid=uuid).first()
        if not req:
            return {"message": "Not found"}, 404
        return req.to_dict(), 200

    def put(self, uuid):
        req = ResearchRequestNew.query.filter_by(uuid=uuid).first()
        if not req:
            return {"message": "Not found"}, 404

        data = request.json

        for key, value in data.items():
            setattr(req, key, value)

        db.session.commit()
        return {"message": "Updated successfully"}, 200

    def delete(self, uuid):
        req = ResearchRequestNew.query.filter_by(uuid=uuid).first()
        if not req:
            return {"message": "Not found"}, 404

        db.session.delete(req)
        db.session.commit()
        return {"message": "Deleted"}, 200

@api.route("/research-requests", methods=["GET"])
class ResearchRequestsList(Resource):
    def get(self):
        requests = ResearchRequestNew.query.order_by(ResearchRequestNew.id.desc()).all()
        return [{
            "uuid": r.uuid,
            "title": r.title,
            "client_name": r.client_name,
            "priority": r.priority,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d"),
        } for r in requests], 200

@api.route("/research-requests/getAll", methods=["GET", "OPTIONS"])
class ResearchRequestsListNew(Resource):
    @cross_origin()
    def options(self):
        return {'Allow': 'GET'}, 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

    @cross_origin()
    def get(self):
        requests = ResearchRequestNew.query.order_by(ResearchRequestNew.id.desc()).all()
        return [r.to_dict() for r in requests], 200