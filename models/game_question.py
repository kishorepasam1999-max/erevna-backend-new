# # models/game_question.py
# import uuid
# from datetime import datetime
# from extensions import db

# class GameQuestion(db.Model):
#     __tablename__ = "game_questions"

#     id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     client_id = db.Column(db.String(36), nullable=False)
#     project_id = db.Column(db.String(36), nullable=False)
#     game_id = db.Column(db.String(36), nullable=False)

#     question = db.Column(db.Text, nullable=False)
#     options = db.Column(db.JSON, nullable=True)
#     status = db.Column(db.String(20), default="Active")
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# models/game_question.py
import uuid
from datetime import datetime
from extensions import db

class GameQuestion(db.Model):
    __tablename__ = "game_questions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), nullable=False)
    project_id = db.Column(db.String(36), nullable=False)
    game_id = db.Column(db.String(36), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if 'options' not in kwargs:
            kwargs['options'] = []
        super().__init__(**kwargs)

    # ✅ ADD THIS EXACTLY HERE
    @property
    def safe_options(self):
        """
        Always return options as a LIST for API response,
        even if DB contains old/bad JSON structure.
        """
        if isinstance(self.options, dict):
            return self.options.get("options", [])
        if isinstance(self.options, list):
            return self.options
        return []

    def __repr__(self):
        return f"<GameQuestion {self.id}: {self.question[:50]}...>"
