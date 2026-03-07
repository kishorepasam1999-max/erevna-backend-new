from extensions import db
from datetime import datetime

class GameMapping(db.Model):
    __tablename__ = "device_game_mapping"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.String(36), nullable=False)
    device_id = db.Column(db.String(36), nullable=False)
    game_id = db.Column(db.String(36), nullable=False)
    mapped_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('location_id', 'device_id', 'game_id', name='uq_mapping'),)

    def to_dict(self):
        return {
            "id": self.id,
            "location_id": self.location_id,
            "device_id": self.device_id,
            "game_id": self.game_id,
            "mapped_at": self.mapped_at.isoformat()
        }
