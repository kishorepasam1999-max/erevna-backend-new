from flask_restx import Namespace, Resource
from flask import request
from extensions import db
from models.response import Response

# Create a namespace for responses
responses_ns = Namespace("responses", description="Survey responses operations")

@responses_ns.route("/<string:game_id>/response")
class GameSurveyResponseResource(Resource):
    def post(self, game_id):
        """
        Store a user's survey response during the game
        """
        data = request.json
        user_id = data.get("user_id")
        question_id = data.get("question_id")
        answer = data.get("answer")

        if not user_id or not question_id or not answer:
            return {"error": "user_id, question_id and answer required"}, 400

        response = Response(
            game_id=game_id,
            user_id=user_id,
            answers={str(question_id): answer}
        )
        db.session.add(response)
        db.session.commit()

        return {"message": "Survey answer saved"}, 201
