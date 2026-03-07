from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.game_mapping import GameMapping

api = Namespace("GameMapping", description="Map Games to Devices and Locations")

# Swagger model
mapping_model = api.model("GameMapping", {
    "location_id": fields.String(required=True),
    "device_ids": fields.List(fields.String, required=True),
    "game_id": fields.String(required=True)
})

# ---------------------------------------------------------
# CREATE / MAP GAMES
# ---------------------------------------------------------
@api.route("/")
class MapGame(Resource):

    @api.expect(mapping_model)
    def post(self):
        data = request.json
        location_id = data["location_id"]
        device_ids = data["device_ids"]
        game_id = data["game_id"]

        mapped_count = 0
        for device_id in device_ids:
            existing = GameMapping.query.filter_by(
                location_id=location_id,
                device_id=device_id,
                game_id=game_id
            ).first()
            if not existing:
                mapping = GameMapping(
                    location_id=location_id,
                    device_id=device_id,
                    game_id=game_id
                )
                db.session.add(mapping)
                mapped_count += 1

        db.session.commit()
        return {"message": f"{mapped_count} devices mapped successfully"}, 201

# ---------------------------------------------------------
# GET ALL MAPPINGS
# ---------------------------------------------------------
@api.route("/list")
class GameMappingList(Resource):
    def get(self):
        mappings = GameMapping.query.order_by(GameMapping.mapped_at.desc()).all()
        return [m.to_dict() for m in mappings], 200

# ---------------------------------------------------------
# GET / DELETE MAPPING BY ID
# ---------------------------------------------------------
@api.route("/<int:id>")
class GameMappingByID(Resource):
    def get(self, id):
        mapping = GameMapping.query.get(id)
        if not mapping:
            return {"message": "Mapping not found"}, 404
        return mapping.to_dict(), 200

    def delete(self, id):
        mapping = GameMapping.query.get(id)
        if not mapping:
            return {"message": "Mapping not found"}, 404
        db.session.delete(mapping)
        db.session.commit()
        return {"message": "Mapping deleted successfully"}, 200
