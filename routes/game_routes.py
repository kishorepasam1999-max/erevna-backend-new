from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.games import Game

api = Namespace("Games", description="Manage Game List")

# ----------------------------------------------------------
# NESTED MODELS (required for Swagger UI)
# ----------------------------------------------------------

feature_item = api.model("FeatureItem", {
    "title": fields.String(required=True),
    "points": fields.List(fields.String)
})

research_item = api.model("ResearchItem", {
    "title": fields.String(required=True),
    "points": fields.List(fields.String)
})

# ----------------------------------------------------------
# MAIN GAME MODEL
# ----------------------------------------------------------

game_model = api.model("Game", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String(readonly=True),

    "game_name": fields.String(required=True),
    "game_type": fields.String,
    "version": fields.String,
    "release_date": fields.String,
    "developer": fields.String,
    "description": fields.String,
    "max_players": fields.Integer,
    "average_duration": fields.String,
    "platforms": fields.List(fields.String),
    "status": fields.String,
    "tags": fields.List(fields.String),
    "rules": fields.String,
    "project_id": fields.String,
    "task_id": fields.String,
    "category": fields.String,
    "game_mode": fields.String,
    "duration": fields.String,

    "game_features": fields.List(fields.Nested(feature_item)),
    "research_applications": fields.List(fields.Nested(research_item)),

    "technical_specializations": fields.String,
    "game_images": fields.List(fields.String),
    "game_video": fields.String,

    "created_at": fields.String,
    "updated_at": fields.String
})

# ----------------------------------------------------------
# GAME LIST ROUTES
# ----------------------------------------------------------

@api.route("")
class GameList(Resource):

    # @api.marshal_list_with(game_model)
    # def get(self):
    #     games = Game.query.order_by(Game.created_at.desc()).all()
    #     return
    @api.marshal_list_with(game_model) 
    def get(self):
        """Get all games"""
        try:
            games = Game.query.order_by(Game.created_at.desc()).all()
            return [game.to_dict() for game in games]
        except Exception as e:
            import traceback
            print("Error in GameList.get():")
            print(traceback.format_exc())
            api.abort(500, f"Error fetching games: {str(e)}")
   
   
    
    @api.expect(game_model)
    @api.marshal_with(game_model, code=201)
    def post(self):
        data = request.json

        game = Game(
        game_name=data.get("game_name"),
        game_type=data.get("game_type"),
        version=data.get("version"),
        release_date=data.get("release_date"),
        developer=data.get("developer"),
        description=data.get("description"),
        max_players=data.get("max_players"),
        average_duration=data.get("average_duration"),
        platforms=data.get("platforms") or [],
        status=data.get("status", "active"),
        tags=data.get("tags") or [],
        rules=data.get("rules"),
        project_id=data.get("project_id"),
        task_id=data.get("task_id"),
        category=data.get("category"),
        game_mode=data.get("game_mode"),
        duration=data.get("duration"),

        # Make sure these are lists
        game_features=data.get("game_features") or [],
        research_applications=data.get("research_applications") or [],

        technical_specializations=data.get("technical_specializations"),
        game_images=data.get("game_images") or [],
        game_video=data.get("game_video"),
        )

        db.session.add(game)
        db.session.commit()
        return game, 201


# ----------------------------------------------------------
# SINGLE GAME ROUTES
# ----------------------------------------------------------

@api.route("/<string:uuid>")
class GameItem(Resource):

    @api.marshal_list_with(game_model)
    def get(self, uuid):
        """Get a single game by UUID"""
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            api.abort(404, "Game not found")
        return game.to_dict()
    

    # @api.marshal_with(game_model)
    # def get(self, uuid):
    #     game = Game.query.filter_by(uuid=uuid).first()
    #     if not game:
    #         return {"message": "Game not found"}, 404
    #     return game
    

    @api.expect(game_model)
    @api.marshal_with(game_model)
    def put(self, uuid):
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            return {"message": "Game not found"}, 404

        data = request.json
        for key, value in data.items():
            if hasattr(game, key):
                setattr(game, key, value)

        db.session.commit()
        return game
   

    @api.response(200, "Game deleted successfully")
    def delete(self, uuid):
        """Delete a game"""
        game = Game.query.filter_by(uuid=uuid).first()
        if not game:
            return {"message": "Game not found"}, 404

        db.session.delete(game)
        db.session.commit()
        return {"message": "Game deleted successfully"}  # dict is fine here
