from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.communication import Communication
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace("communications", description="Communications endpoints")

comm_in = api.model("CommunicationIn", {
    "thread_title": fields.String(required=True),
    "status": fields.String,
    "messages_count": fields.Integer
})

@api.route("/")
class CommList(Resource):
    def get(self):
        args = request.args
        q = Communication.query
        if args.get("status"):
            q = q.filter_by(status=args.get("status"))
        items = q.order_by(Communication.created_at.desc()).all()
        return [c.to_dict() for c in items]

    @jwt_required()
    @api.expect(comm_in)
    def post(self):
        payload = request.json
        c = Communication(
            thread_title=payload["thread_title"],
            status=payload.get("status","open"),
            messages_count=payload.get("messages_count",0)
        )
        db.session.add(c)
        db.session.commit()
        return {"uuid": c.uuid}, 201
