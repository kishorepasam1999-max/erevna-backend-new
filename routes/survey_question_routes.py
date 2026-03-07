from flask_restx import Namespace, Resource, fields
from models import SurveyQuestion

# Create namespace
surveys_ns = Namespace("surveys", description="Survey questions operations")

# Optional: Swagger model for question
question_model = surveys_ns.model(
    "SurveyQuestion",
    {
        "id": fields.Integer(description="Question ID"),
        "question_text": fields.String(description="Question text"),
        "options": fields.Raw(description="Options array"),
    }
)

# Route to get questions for a specific game
@surveys_ns.route("/game/<string:game_id>")
class GameQuestionsResource(Resource):
    @surveys_ns.marshal_list_with(question_model)
    def get(self, game_id):
        """
        Fetch all survey questions for a specific game.
        """
        questions = SurveyQuestion.query.filter_by(game_id=game_id).all()
        return questions, 200
