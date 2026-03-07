# from extensions import db
# import uuid
# from datetime import datetime
# import json
# from sqlalchemy import TypeDecorator

# # class SafeJSON(TypeDecorator):
# #     """A JSON type that handles invalid JSON gracefully."""
# #     impl = db.JSON  # Use the underlying JSON type
# #     def process_result_value(self, value, dialect):
# #         if value is None:
# #             return None
# #         try:
# #             if isinstance(value, str):
# #                 return json.loads(value) if value.strip() else {}
# #             return value
# #         except (json.JSONDecodeError, TypeError):
# #             return {}

# def generate_uuid():
#     return str(uuid.uuid4())


# class Game(db.Model):
#     __tablename__ = "games"

#     id = db.Column(db.Integer, primary_key=True)
#     uuid = db.Column(db.String(36), unique=True, default=generate_uuid)

#     game_name = db.Column(db.String(255), nullable=False)
#     game_type = db.Column(db.String(255))
#     version = db.Column(db.String(50))
#     release_date = db.Column(db.Date)
#     developer = db.Column(db.String(255))
#     description = db.Column(db.Text)
#     max_players = db.Column(db.Integer)
#     average_duration = db.Column(db.String(100))
#     platforms = db.Column(db.JSON)
#     # platforms = db.Column(SafeJSON, default=None)
#     status = db.Column(db.String(50), default="active")
#     tags = db.Column(db.JSON)
#     # tags = db.Column(SafeJSON, default=None)
#     rules = db.Column(db.Text)

#     project_id = db.Column(db.String(100))
#     task_id = db.Column(db.String(100))
#     category = db.Column(db.String(255))
#     game_mode = db.Column(db.String(255))
#     duration = db.Column(db.String(100))
    
#     # Ensure JSON-serializable values
#     game_features = db.Column(db.JSON, default=[])
#     # game_features = db.Column(db.JSON, default=None)
#     research_applications = db.Column(db.JSON, default=[])
#     # research_applications = db.Column(db.JSON, default=None)
#     technical_specializations = db.Column(db.Text)

#     game_images = db.Column(db.JSON, default=[])
#     # game_images = db.Column(SafeJSON, default=None)
#     game_video = db.Column(db.String(255))

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     def __repr__(self):
#         return f"<Game {self.game_name}>"

#     # helper to ensure proper JSON serialization
#     def serialize(self):
#         return {
#             "id": self.id,
#             "uuid": self.uuid,
#             "game_name": self.game_name,
#             "game_type": self.game_type,
#             "version": self.version,
#             "release_date": self.release_date.isoformat() if self.release_date else None,
#             "developer": self.developer,
#             "description": self.description,
#             "max_players": self.max_players,
#             "average_duration": self.average_duration,
#             "platforms": self.platforms or [],
#             "status": self.status,
#             "tags": self.tags or [],
#             "rules": self.rules,
#             "project_id": self.project_id,
#             "task_id": self.task_id,
#             "category": self.category,
#             "game_mode": self.game_mode,
#             "duration": self.duration,
#             "game_features": self.game_features or [],
#             "research_applications": self.research_applications or [],
#             "technical_specializations": self.technical_specializations,
#             "game_images": self.game_images or [],
#             "game_video": self.game_video,
#             "created_at": self.created_at.isoformat(),
#             "updated_at": self.updated_at.isoformat(),
#         }

from extensions import db
from datetime import datetime
import uuid
import json
from sqlalchemy import TypeDecorator

def generate_uuid():
    return str(uuid.uuid4())

class SafeJSON(TypeDecorator):
    """A JSON type that handles invalid JSON gracefully."""
    impl = db.JSON

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            return json.dumps(value) if not isinstance(value, str) else value
        except (TypeError, ValueError):
            return None

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            if isinstance(value, str):
                return json.loads(value) if value.strip() else {}
            return value
        except (json.JSONDecodeError, TypeError):
            return {}

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    game_name = db.Column(db.String(255), nullable=False)
    game_type = db.Column(db.String(100))
    version = db.Column(db.String(50))
    release_date = db.Column(db.Date)
    developer = db.Column(db.String(255))
    description = db.Column(db.Text)
    max_players = db.Column(db.Integer)
    average_duration = db.Column(db.String(100))
    platforms = db.Column(SafeJSON, default=list)
    status = db.Column(db.String(50), default="active")
    tags = db.Column(SafeJSON, default=list)
    rules = db.Column(db.Text)
    project_id = db.Column(db.String(100))
    task_id = db.Column(db.String(100))
    category = db.Column(db.String(100))
    game_mode = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    game_features = db.Column(SafeJSON, default=list)
    research_applications = db.Column(SafeJSON, default=list)
    technical_specializations = db.Column(db.Text)
    game_images = db.Column(SafeJSON, default=list)
    game_video = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Game {self.game_name}>"

    def to_dict(self):
        """Convert game object to dictionary"""
        return {
            "id": self.id,
            "uuid": str(self.uuid) if self.uuid else None,
            "game_name": self.game_name,
            "game_type": self.game_type,
            "version": self.version,
            "release_date": str(self.release_date) if self.release_date else None,
            "developer": self.developer,
            "description": self.description,
            "max_players": self.max_players,
            "average_duration": self.average_duration,
            "platforms": self.platforms if isinstance(self.platforms, (list, dict)) else [],
            "status": self.status,
            "tags": self.tags if isinstance(self.tags, (list, dict)) else [],
            "rules": self.rules,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "category": self.category,
            "game_mode": self.game_mode,
            "duration": self.duration,
            "game_features": self.game_features if isinstance(self.game_features, (list, dict)) else [],
            "research_applications": self.research_applications if isinstance(self.research_applications, (list, dict)) else [],
            "technical_specializations": self.technical_specializations,
            "game_images": self.game_images if isinstance(self.game_images, (list, dict)) else [],
            "game_video": self.game_video,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }