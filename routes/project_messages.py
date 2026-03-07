from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.message import Message
from models.project import Project
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace("project_messages", description="Project messages")

msg_in = api.model("ProjectMessageIn", {
    "project_uuid": fields.String(required=True),
    "content": fields.String(required=True),
    "sender_uuid": fields.String
})

@api.route("/")
class MessageList(Resource):
    def get(self):
        project_uuid = request.args.get("project_uuid")
        q = Message.query
        if project_uuid:
            q = q.filter_by(communication_uuid=project_uuid)  # note: using communication_uuid field or adapt to project message model
        items = q.order_by(Message.created_at.asc()).all()
        return [m.to_dict() for m in items]

    @jwt_required()
    @api.expect(msg_in)
    def post(self):
        payload = request.json
        m = Message(
            communication_uuid = payload.get("project_uuid"),
            content = payload["content"],
            sender_uuid = payload.get("sender_uuid")
        )
        db.session.add(m)
        # if you want to increment messages_count on Communication do it here
        db.session.commit()
        return {"uuid": m.uuid}, 201
