
from extensions import db

class GameMove(db.Model):
    __tablename__ = "game_moves"
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey("games.uuid"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("registrations.id"), nullable=False)
    move = db.Column(db.JSON, nullable=False)  # {from: x, to: y, dice: z}
    timestamp = db.Column(db.DateTime, default=db.func.now())
