from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models import GameMove

# Namespace
gamemoves_ns = Namespace("gamemoves", description="Game moves operations")

# Swagger model for request body
move_model = gamemoves_ns.model(
    "GameMove",
    {
        "user_id": fields.Integer(required=True, description="ID of the player making the move"),
        "move": fields.Nested(
            gamemoves_ns.model(
                "MoveDetail",
                {
                    "from": fields.Integer(required=True, description="Starting position"),
                    "to": fields.Integer(required=True, description="Ending position"),
                    "dice": fields.Integer(required=True, description="Dice roll value")
                }
            ),
            required=True,
            description="Move details"
        )
    }
)

# Route
@gamemoves_ns.route("/<string:game_id>/move")
class GameMoveResource(Resource):
    @gamemoves_ns.expect(move_model)
    def post(self, game_id):
        """
        Store a user's move during a Snake & Ladder game.
        """
        # Ensure request is JSON
        if not request.is_json:
            return {"error": "Request body must be JSON"}, 400

        data = request.get_json()
        user_id = data.get("user_id")
        move = data.get("move")

        if not user_id or not move:
            return {"error": "user_id and move required"}, 400

        # Save to DB
        game_move = GameMove(game_id=game_id, user_id=user_id, move=move)
        db.session.add(game_move)
        db.session.commit()

        return {"message": "Move saved"}, 201
