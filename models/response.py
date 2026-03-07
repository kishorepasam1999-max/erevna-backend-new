from extensions import db

class Response(db.Model):
    __tablename__ = "responses"
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey("games.uuid"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("registrations.id"), nullable=False)
    answers = db.Column(db.JSON, nullable=False)