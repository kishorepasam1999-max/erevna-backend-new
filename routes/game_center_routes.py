from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.games import Game
from models.user import User
from datetime import datetime
import uuid

api = Namespace("Game Center", description="Game Center Management")

# ----------------------------------------------------------
# NESTED MODELS (required for Swagger UI)
# ----------------------------------------------------------

game_info_model = api.model("GameInfo", {
    "id": fields.Integer(readonly=True),
    "game_name": fields.String(required=True),
    "description": fields.String,
    "game_url": fields.String,
    "game_file_size": fields.Integer,
    "game_version": fields.String,
    "min_os_version": fields.String,
    "game_category": fields.String,
    "is_active": fields.Boolean,
})

user_game_installation_model = api.model("UserGameInstallation", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String(readonly=True),
    "user_id": fields.Integer(readonly=True),
    "game_id": fields.Integer(readonly=True),
    "install_status": fields.String(readonly=True),
    "install_date": fields.String(readonly=True),
    "last_played": fields.String(readonly=True),
    "play_count": fields.Integer(readonly=True),
    "current_level": fields.Integer(readonly=True),
    "high_score": fields.Integer(readonly=True),
    "total_playtime": fields.Integer(readonly=True),
    "device_id": fields.String(readonly=True),
    "created_at": fields.String(readonly=True),
    "updated_at": fields.String(readonly=True),
})

# ----------------------------------------------------------
# GAME CENTER ENDPOINTS
# ----------------------------------------------------------

@api.route("/game-center/games")
class GetAvailableGames(Resource):
    @api.doc("get_available_games")
    @api.marshal_list_with(game_info_model)
    def get(self):
        """Get all available games"""
        try:
            games = Game.query.filter_by(is_active=True).all()
            game_list = []
            for game in games:
                game_list.append({
                    'id': game.id,
                    'game_name': game.game_name,
                    'description': game.description,
                    'game_url': game.game_url,
                    'game_file_size': game.game_file_size,
                    'game_version': game.version,
                    'min_os_version': game.min_android_version,
                    'game_category': game.category,
                    'is_active': game.is_active
                })
            return {"success": True, "games": game_list}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/my-games")
class GetMyGames(Resource):
    @api.doc("get_my_games")
    @api.marshal_list_with(user_game_installation_model)
    @api.doc(security='Bearer')
    def get(self):
        """Get user's installed games"""
        try:
            # This would need user authentication - for now return mock data
            return {"success": True, "games": []}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/install/<int:gameId>")
class InstallGame(Resource):
    @api.doc("install_game")
    @api.expect(game_info_model)
    @api.doc(security='Bearer')
    def post(self, gameId):
        """Install a game"""
        try:
            game = Game.query.get(gameId)
            if not game:
                return {"success": False, "message": "Game not found"}, 404
            
            # Create installation record (simplified)
            installation = {
                'id': 1,
                'uuid': str(uuid.uuid4()),
                'user_id': 1,  # Would get from JWT token
                'game_id': gameId,
                'install_status': 'installing',
                'install_date': datetime.utcnow().isoformat(),
                'last_played': None,
                'play_count': 0,
                'current_level': 1,
                'high_score': 0,
                'total_playtime': 0,
                'device_id': None,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return {"success": True, "message": "Game installation started", "installation": installation}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/complete-installation/<int:gameId>")
class CompleteInstallation(Resource):
    @api.doc("complete_installation")
    @api.doc(security='Bearer')
    def post(self, gameId):
        """Complete game installation"""
        try:
            return {"success": True, "message": "Game installation completed successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/launch/<int:gameId>")
class LaunchGame(Resource):
    @api.doc("launch_game")
    @api.doc(security='Bearer')
    def post(self, gameId):
        """Launch a game"""
        try:
            game = Game.query.get(gameId)
            if not game:
                return {"success": False, "message": "Game not found"}, 404
            
            return {
                "success": True, 
                "message": "Game launched successfully",
                "launch_url": f"game://{game.uuid}",
                "installation": {
                    "id": 1,
                    "game_id": gameId,
                    "install_status": "installed"
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/update-progress/<int:gameId>")
class UpdateGameProgress(Resource):
    @api.doc("update_game_progress")
    @api.doc(security='Bearer')
    def put(self, gameId):
        """Update game progress"""
        try:
            data = request.get_json()
            return {"success": True, "message": "Game progress updated successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-center/status/<int:gameId>")
class GetInstallationStatus(Resource):
    @api.doc("get_installation_status")
    @api.doc(security='Bearer')
    def get(self, gameId):
        """Get installation status"""
        try:
            return {
                "success": True,
                "status": "installed",
                "installation": {
                    "id": 1,
                    "game_id": gameId,
                    "install_status": "installed"
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
