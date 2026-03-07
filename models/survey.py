from extensions import db

class SurveyQuestion(db.Model):
    __tablename__ = "survey_questions"
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(255), db.ForeignKey("games.uuid"), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON, nullable=False)  # store options as JSON array

    def __repr__(self):
        return f"<SurveyQuestion {self.id}: {self.question_text}>"
