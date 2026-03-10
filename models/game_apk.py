from extensions import db
from datetime import datetime
import uuid
import os

def generate_uuid():
    return str(uuid.uuid4())

class GameAPK(db.Model):
    """Game APK files model for storing APK information"""
    __tablename__ = 'game_apks'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    
    # APK File Information
    apk_name = db.Column(db.String(255), nullable=False)
    apk_file_path = db.Column(db.String(500), nullable=False)  # Server storage path
    apk_url = db.Column(db.String(500), nullable=False)  # Download URL
    apk_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    
    # Version Information
    apk_version = db.Column(db.String(50), nullable=False)
    apk_build_number = db.Column(db.Integer, nullable=False)
    min_android_version = db.Column(db.String(50), nullable=False)
    target_android_version = db.Column(db.String(50), nullable=False)
    
    # APK Metadata
    package_name = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.Text)  # JSON string of permissions
    signature_hash = db.Column(db.String(255))  # APK signature for security
    
    # Status and Tracking
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    install_count = db.Column(db.Integer, default=0)
    
    # Relationships
    game = db.relationship('Game', backref=db.backref('apks', lazy=True))
    installations = db.relationship('APKInstallation', backref='apk', lazy=True)
    
    def __repr__(self):
        return f"<GameAPK {self.apk_name} v{self.apk_version}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid) if self.uuid else None,
            "game_id": self.game_id,
            "apk_name": self.apk_name,
            "apk_url": self.apk_url,
            "apk_size": self.apk_size,
            "apk_version": self.apk_version,
            "apk_build_number": self.apk_build_number,
            "min_android_version": self.min_android_version,
            "target_android_version": self.target_android_version,
            "package_name": self.package_name,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "upload_date": str(self.upload_date) if self.upload_date else None,
            "download_count": self.download_count,
            "install_count": self.install_count,
            "game": self.game.to_dict() if self.game else None
        }

class APKInstallation(db.Model):
    """Track user installations of APKs"""
    __tablename__ = 'apk_installations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    apk_id = db.Column(db.Integer, db.ForeignKey('game_apks.id'), nullable=False)
    
    # Installation Status
    install_status = db.Column(db.String(50), default='pending')  # pending, downloading, installing, installed, failed
    download_progress = db.Column(db.Integer, default=0)  # 0-100
    install_progress = db.Column(db.Integer, default=0)  # 0-100
    
    # Installation Details
    install_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.String(255))
    device_info = db.Column(db.Text)  # JSON string of device info
    
    # Usage Tracking
    last_played = db.Column(db.DateTime)
    play_count = db.Column(db.Integer, default=0)
    total_playtime = db.Column(db.Integer, default=0)  # in seconds
    
    # Relationships
    user = db.relationship('User', backref=db.backref('apk_installations', lazy=True))
    game = db.relationship('Game', backref=db.backref('installations', lazy=True))
    
    def __repr__(self):
        return f"<APKInstallation {self.user_id}:{self.apk_id} {self.install_status}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "uuid": str(self.uuid) if self.uuid else None,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "apk_id": self.apk_id,
            "install_status": self.install_status,
            "download_progress": self.download_progress,
            "install_progress": self.install_progress,
            "install_date": str(self.install_date) if self.install_date else None,
            "last_updated": str(self.last_updated) if self.last_updated else None,
            "device_id": self.device_id,
            "last_played": str(self.last_played) if self.last_played else None,
            "play_count": self.play_count,
            "total_playtime": self.total_playtime,
            "apk": self.apk.to_dict() if self.apk else None,
            "game": self.game.to_dict() if self.game else None
        }
