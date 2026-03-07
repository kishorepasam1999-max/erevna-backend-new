from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.games import Game
from models.user import User
from datetime import datetime
import uuid
import os

api = Namespace("Game APK", description="Game APK Management")

# ----------------------------------------------------------
# NESTED MODELS (required for Swagger UI)
# ----------------------------------------------------------

game_apk_model = api.model("GameAPK", {
    "id": fields.Integer(readonly=True),
    "game_id": fields.Integer(readonly=True),
    "apk_name": fields.String(readonly=True),
    "apk_url": fields.String(readonly=True),
    "apk_size": fields.Integer(readonly=True),
    "apk_version": fields.String(readonly=True),
    "apk_build_number": fields.Integer(readonly=True),
    "min_android_version": fields.String(readonly=True),
    "target_android_version": fields.String(readonly=True),
    "permissions": fields.String(readonly=True),
    "is_active": fields.Boolean(readonly=True),
    "upload_date": fields.String(readonly=True),
    "download_count": fields.Integer(readonly=True),
    "install_count": fields.Integer(readonly=True),
})

apk_installation_model = api.model("APKInstallation", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String(readonly=True),
    "user_id": fields.Integer(readonly=True),
    "game_id": fields.Integer(readonly=True),
    "apk_id": fields.Integer(readonly=True),
    "install_status": fields.String(readonly=True),
    "download_progress": fields.Integer(readonly=True),
    "install_progress": fields.Integer(readonly=True),
    "install_date": fields.String(readonly=True),
    "last_updated": fields.String(readonly=True),
    "device_id": fields.String(readonly=True),
    "last_played": fields.String(readonly=True),
    "play_count": fields.Integer(readonly=True),
    "total_playtime": fields.Integer(readonly=True),
})

# ----------------------------------------------------------
# GAME APK ENDPOINTS
# ----------------------------------------------------------

@api.route("/game-apk/upload")
class UploadAPK(Resource):
    @api.doc("upload_apk")
    @api.expect(game_apk_model)
    @api.doc(security='Bearer')
    def post(self):
        """Upload APK file"""
        try:
            if 'file' not in request.files:
                return {"success": False, "message": "No file provided"}, 400
            
            file = request.files['file']
            game_id = request.form.get('game_id')
            apk_version = request.form.get('apk_version')
            min_android_version = request.form.get('min_android_version')
            target_android_version = request.form.get('target_android_version')
            
            if not game_id:
                return {"success": False, "message": "Game ID is required"}, 400
            
            # Save file (simplified - in production use cloud storage)
            filename = f"{game_id}_{apk_version}_{file.filename}"
            file_path = os.path.join('uploads', filename)
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            file.save(file_path)
            
            # Create APK record
            apk_record = {
                'id': 1,
                'game_id': int(game_id),
                'apk_name': filename,
                'apk_url': f"/uploads/{filename}",
                'apk_size': os.path.getsize(file_path),
                'apk_version': apk_version,
                'apk_build_number': 1,
                'min_android_version': min_android_version,
                'target_android_version': target_android_version,
                'permissions': "android.permission.INTERNET",
                'is_active': True,
                'upload_date': datetime.utcnow().isoformat(),
                'download_count': 0,
                'install_count': 0
            }
            
            return {"success": True, "message": "APK uploaded successfully", "apk": apk_record}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/list")
class GetAvailableAPKs(Resource):
    @api.doc("get_available_apks")
    @api.marshal_list_with(game_apk_model)
    def get(self):
        """Get available APKs"""
        try:
            # Return mock data for now
            return {"success": True, "apks": []}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/my-installations")
class GetMyInstallations(Resource):
    @api.doc("get_my_installations")
    @api.marshal_list_with(apk_installation_model)
    @api.doc(security='Bearer')
    def get(self):
        """Get user's APK installations"""
        try:
            return {"success": True, "installations": []}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/install/<int:apk_id>")
class InstallAPK(Resource):
    @api.doc("install_apk")
    @api.doc(security='Bearer')
    def post(self, apk_id):
        """Install APK"""
        try:
            installation = {
                'id': 1,
                'uuid': str(uuid.uuid4()),
                'user_id': 1,
                'game_id': apk_id,
                'apk_id': apk_id,
                'install_status': 'downloading',
                'download_progress': 0,
                'install_progress': 0,
                'install_date': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'device_id': None,
                'last_played': None,
                'play_count': 0,
                'total_playtime': 0
            }
            
            return {"success": True, "message": "APK installation started", "installation": installation}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/update-progress/<int:installation_id>")
class UpdateProgress(Resource):
    @api.doc("update_progress")
    @api.doc(security='Bearer')
    def put(self, installation_id):
        """Update installation progress"""
        try:
            data = request.get_json()
            return {"success": True, "message": "Progress updated successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/launch/<int:installation_id>")
class LaunchGame(Resource):
    @api.doc("launch_game_from_apk")
    @api.doc(security='Bearer')
    def post(self, installation_id):
        """Launch game from APK"""
        try:
            return {
                "success": True,
                "message": "Game launched successfully",
                "game_info": {
                    "id": installation_id,
                    "name": "Game Name",
                    "version": "1.0.0"
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/game-apk/download/<string:filename>")
class DownloadAPK(Resource):
    @api.doc("download_apk")
    def get(self, filename):
        """Download APK file"""
        try:
            file_path = os.path.join('uploads', filename)
            if os.path.exists(file_path):
                return {"success": True, "download_url": f"/uploads/{filename}"}
            else:
                return {"success": False, "message": "File not found"}, 404
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
