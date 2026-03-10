from flask_restx import Namespace, Resource, fields
from flask import request, send_file
from extensions import db
from models.games import Game
from models.game_apk import GameAPK, APKInstallation
from models.user import User
from datetime import datetime
import uuid
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace("game_apk", description="Game APK Management")

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

@api.route("/upload")
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
            apk_version = request.form.get('apk_version', '1.0.0')
            min_android_version = request.form.get('min_android_version', '5.0')
            target_android_version = request.form.get('target_android_version', '13')
            
            if not game_id:
                return {"success": False, "message": "Game ID is required"}, 400
            
            # Check if game exists
            game = Game.query.get(game_id)
            if not game:
                return {"success": False, "message": "Game not found"}, 404
            
            # Save file
            filename = f"{game_id}_{apk_version}_{file.filename}"
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            file_path = os.path.join(upload_dir, filename)
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file.save(file_path)
            
            # Create APK record
            apk = GameAPK(
                game_id=int(game_id),
                apk_name=filename,
                apk_file_path=file_path,
                apk_url=f"/game-apk/download/{filename}",
                apk_size=os.path.getsize(file_path),
                apk_version=apk_version,
                apk_build_number=1,
                min_android_version=min_android_version,
                target_android_version=target_android_version,
                package_name=f"com.erevna.game{game_id}",
                permissions="android.permission.INTERNET,android.permission.WRITE_EXTERNAL_STORAGE"
            )
            
            db.session.add(apk)
            db.session.commit()
            
            return {"success": True, "message": "APK uploaded successfully", "apk": apk.to_dict()}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/list")
class GetAvailableAPKs(Resource):
    @api.doc("get_available_apks")
    def get(self):
        """Get available APKs"""
        try:
            apks = GameAPK.query.filter_by(is_active=True, is_public=True).all()
            return {"success": True, "apks": [apk.to_dict() for apk in apks]}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/my-installations")
class GetMyInstallations(Resource):
    @api.doc("get_my_installations")
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self):
        """Get user's APK installations"""
        try:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            installations = APKInstallation.query.filter_by(user_id=user_id).all()
            return {"success": True, "installations": [inst.to_dict() for inst in installations]}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/install/<int:apk_id>")
class InstallAPK(Resource):
    @api.doc("install_apk")
    @api.doc(security='Bearer')
    @jwt_required()
    def post(self, apk_id):
        """Install APK"""
        try:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            # Check if APK exists
            apk = GameAPK.query.get(apk_id)
            if not apk:
                return {"success": False, "message": "APK not found"}, 404
            
            # Check if already installed
            existing_install = APKInstallation.query.filter_by(
                user_id=user_id, 
                apk_id=apk_id, 
                install_status='installed'
            ).first()
            
            if existing_install:
                return {"success": False, "message": "APK already installed"}, 400
            
            # Create installation record
            installation = APKInstallation(
                user_id=user_id,
                game_id=apk.game_id,
                apk_id=apk_id,
                install_status='downloading',
                device_id=request.form.get('device_id', 'unknown')
            )
            
            db.session.add(installation)
            db.session.commit()
            
            # Increment download count
            apk.download_count += 1
            db.session.commit()
            
            return {"success": True, "message": "APK installation started", "installation": installation.to_dict()}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/update-progress/<int:installation_id>")
class UpdateProgress(Resource):
    @api.doc("update_progress")
    @api.doc(security='Bearer')
    def put(self, installation_id):
        """Update installation progress"""
        try:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            data = request.get_json()
            installation = APKInstallation.query.filter_by(
                id=installation_id, 
                user_id=user_id
            ).first()
            
            if not installation:
                return {"success": False, "message": "Installation not found"}, 404
            
            # Update progress
            if 'download_progress' in data:
                installation.download_progress = data['download_progress']
            
            if 'install_progress' in data:
                installation.install_progress = data['install_progress']
            
            if 'install_status' in data:
                installation.install_status = data['install_status']
                if data['install_status'] == 'installed':
                    installation.install_date = datetime.utcnow()
                    # Increment install count
                    installation.apk.install_count += 1
            
            installation.last_updated = datetime.utcnow()
            db.session.commit()
            
            return {"success": True, "message": "Progress updated successfully", "installation": installation.to_dict()}
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/launch/<int:installation_id>")
class LaunchGame(Resource):
    @api.doc("launch_game_from_apk")
    @api.doc(security='Bearer')
    def post(self, installation_id):
        """Launch game from APK"""
        try:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            installation = APKInstallation.query.filter_by(
                id=installation_id, 
                user_id=user_id,
                install_status='installed'
            ).first()
            
            if not installation:
                return {"success": False, "message": "Game installation not found"}, 404
            
            # Update play statistics
            installation.last_played = datetime.utcnow()
            installation.play_count += 1
            db.session.commit()
            
            return {
                "success": True,
                "message": "Game launched successfully",
                "game_info": {
                    "id": installation.game_id,
                    "name": installation.game.game_name if installation.game else "Unknown Game",
                    "package_name": installation.apk.package_name,
                    "version": installation.apk.apk_version
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

@api.route("/download/<string:filename>")
class DownloadAPK(Resource):
    @api.doc("download_apk")
    def get(self, filename):
        """Download APK file"""
        try:
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            file_path = os.path.join(upload_dir, filename)
            
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=filename)
            else:
                return {"success": False, "message": "File not found"}, 404
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
