from flask_restx import Namespace, Resource
from sqlalchemy import text
from extensions import db
from flask import request
import json

api = Namespace(
    "client-report",
    description="Client gameplay report"
)

@api.route("/summary/<string:client_id>")
class ClientReportSummary(Resource):
    def get(self, client_id):
        """
        Returns:
        user_name, project_name(s), store_name(s), device_name(s), game_name(s)
        filtered by client_id
        """

        query = text("""
            SELECT
                r.user_name,
                GROUP_CONCAT(DISTINCT p.project_name ORDER BY p.project_name) AS project_names,
                GROUP_CONCAT(DISTINCT l.store_name ORDER BY l.store_name) AS location_names,
                GROUP_CONCAT(DISTINCT d.device_model ORDER BY d.device_model) AS device_names,
                GROUP_CONCAT(DISTINCT g.game_name ORDER BY g.game_name) AS game_names
            FROM registrations r

            LEFT JOIN projects p
                ON JSON_CONTAINS(r.project_ids, JSON_QUOTE(p.project_id))

            LEFT JOIN locations l
                ON JSON_CONTAINS(r.location_ids, JSON_QUOTE(l.location_id))

            LEFT JOIN devices d
                ON JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(d.device_id))

            LEFT JOIN games g
                ON JSON_CONTAINS(r.game_ids, JSON_QUOTE(g.uuid))

            WHERE r.client_id = :client_id

            GROUP BY r.id, r.user_name
        """)

        result = db.session.execute(query, {"client_id": client_id})

        data = [
            {
                "user_name": row.user_name,
                "projects": row.project_names.split(",") if row.project_names else [],
                "locations": row.location_names.split(",") if row.location_names else [],
                "devices": row.device_names.split(",") if row.device_names else [],
                "games": row.game_names.split(",") if row.game_names else []
            }
            for row in result
        ]

        return {
            "client_id": client_id,
            "count": len(data),
            "data": data
        }, 200

@api.route("/summary/<string:client_id>/<string:project_id>")
class ClientReportByProject(Resource):
    def get(self, client_id, project_id):
        """
        Returns:
        user_name, location(s), device(s), game(s)
        filtered by client_id and project_id
        """

        query = text("""
            SELECT
                r.user_name,
                GROUP_CONCAT(DISTINCT l.store_name ORDER BY l.store_name) AS location_names,
                GROUP_CONCAT(DISTINCT d.device_model ORDER BY d.device_model) AS device_names,
                GROUP_CONCAT(DISTINCT g.game_name ORDER BY g.game_name) AS game_names
            FROM registrations r

            LEFT JOIN locations l
                ON JSON_CONTAINS(r.location_ids, JSON_QUOTE(l.location_id))

            LEFT JOIN devices d
                ON JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(d.device_id))

            LEFT JOIN games g
                ON JSON_CONTAINS(r.game_ids, JSON_QUOTE(g.uuid))

            WHERE r.client_id = :client_id
              AND JSON_CONTAINS(r.project_ids, JSON_QUOTE(:project_id))

            GROUP BY r.id, r.user_name
        """)

        result = db.session.execute(query, {"client_id": client_id, "project_id": project_id})

        data = [
            {
                "user_name": row.user_name,
                "locations": row.location_names.split(",") if row.location_names else [],
                "devices": row.device_names.split(",") if row.device_names else [],
                "games": row.game_names.split(",") if row.game_names else []
            }
            for row in result
        ]

        return {
            "client_id": client_id,
            "project_id": project_id,
            "count": len(data),
            "data": data
        }, 200

@api.route("/summary/<string:client_id>/<string:project_id>/<string:location_id>")
class ClientReportByLocation(Resource):
    def get(self, client_id, project_id, location_id):
        """
        Returns:
        user_name, devices, games
        filtered by client_id, project_id, and location_id
        """

        query = text("""
            SELECT
                r.user_name,
                GROUP_CONCAT(DISTINCT d.device_model ORDER BY d.device_model) AS device_names,
                GROUP_CONCAT(DISTINCT g.game_name ORDER BY g.game_name) AS game_names
            FROM registrations r

            LEFT JOIN devices d
                ON JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(d.device_id))
                AND d.location_id = :location_id

            LEFT JOIN games g
                ON JSON_CONTAINS(r.game_ids, JSON_QUOTE(g.uuid))

            WHERE r.client_id = :client_id
              AND JSON_CONTAINS(r.project_ids, JSON_QUOTE(:project_id))

            GROUP BY r.id, r.user_name
        """)

        result = db.session.execute(
            query,
            {"client_id": client_id, "project_id": project_id, "location_id": location_id}
        )

        data = [
            {
                "user_name": row.user_name,
                "devices": row.device_names.split(",") if row.device_names else [],
                "games": row.game_names.split(",") if row.game_names else []
            }
            for row in result
        ]

        return {
            "client_id": client_id,
            "project_id": project_id,
            "location_id": location_id,
            "count": len(data),
            "data": data
        }, 200

@api.route("/summary/<string:client_id>/<string:project_id>/<string:location_id>/<string:device_id>")
class ClientReportByDevice(Resource):
    def get(self, client_id, project_id, location_id, device_id):
        """
        Returns:
        user_name and games filtered by client_id, project_id, location_id, and device_id
        """

        query = text("""
            SELECT
                r.user_name,
                GROUP_CONCAT(DISTINCT g.game_name ORDER BY g.game_name) AS game_names
            FROM registrations r

            LEFT JOIN devices d
                ON JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(d.device_id))
                AND d.location_id = :location_id
                AND d.device_id = :device_id

            LEFT JOIN games g
                ON JSON_CONTAINS(r.game_ids, JSON_QUOTE(g.uuid))

            WHERE r.client_id = :client_id
              AND JSON_CONTAINS(r.project_ids, JSON_QUOTE(:project_id))
              AND JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(:device_id))

            GROUP BY r.id, r.user_name
        """)

        result = db.session.execute(
            query,
            {
                "client_id": client_id,
                "project_id": project_id,
                "location_id": location_id,
                "device_id": device_id
            }
        )

        data = [
            {
                "user_name": row.user_name,
                "games": row.game_names.split(",") if row.game_names else []
            }
            for row in result
        ]

        return {
            "client_id": client_id,
            "project_id": project_id,
            "location_id": location_id,
            "device_id": device_id,
            "count": len(data),
            "data": data
        }, 200




# @api.route("/summary/<string:client_id>/<string:project_id>/<string:location_id>/<string:device_id>/<string:game_id>")
# class ClientReportByGame(Resource):
#     def get(self, client_id, project_id, location_id, device_id, game_id):
#         """
#         Returns user_name, game_name, and properly parsed answers
#         filtered by client_id, project_id, location_id, device_id, game_id
#         """

#         query = text("""
#             SELECT
#                 r.user_name,
#                 g.game_name,
#                 res.answers
#             FROM registrations r
#             JOIN responses res
#                 ON res.user_id = r.id
#                 AND res.game_id = :game_id
#             JOIN games g
#                 ON g.uuid = res.game_id
#             WHERE r.client_id = :client_id
#               AND JSON_CONTAINS(r.project_ids, JSON_QUOTE(:project_id))
#               AND JSON_CONTAINS(r.location_ids, JSON_QUOTE(:location_id))
#               AND JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(:device_id))
#               AND JSON_CONTAINS(r.game_ids, JSON_QUOTE(:game_id))
#         """)

#         result = db.session.execute(
#             query,
#             {
#                 "client_id": client_id,
#                 "project_id": project_id,
#                 "location_id": location_id,
#                 "device_id": device_id,
#                 "game_id": game_id
#             }
#         )

#         data = []
#         for row in result:
#             # Parse answers JSON string into Python dict
#             try:
#                 answers = json.loads(row.answers) if row.answers else {}
#             except json.JSONDecodeError:
#                 answers = {}
            
#             data.append({
#                 "user_name": row.user_name,
#                 "game_name": row.game_name,
#                 "answers": answers
#             })

#         return {
#             "client_id": client_id,
#             "project_id": project_id,
#             "location_id": location_id,
#             "device_id": device_id,
#             "game_id": game_id,
#             "count": len(data),
#             "data": data
#         }, 200


@api.route("/summary/<string:client_id>/<string:project_id>/<string:location_id>/<string:device_id>/<string:game_id>")
class ClientReportByGame(Resource):
    def get(self, client_id, project_id, location_id, device_id, game_id):
        """
        Returns user_name, game_name, survey questions and answers
        filtered by client_id, project_id, location_id, device_id, game_id
        """
        # First, get all survey questions for the game
        questions_query = text("""
            SELECT 
                id, 
                question_text, 
                options as question_options
            FROM survey_questions
            WHERE game_id = :game_id
            ORDER BY id
        """)

        questions_result = db.session.execute(
            questions_query,
            {"game_id": game_id}
        )

        # Parse the JSON options string into a Python list
        questions = {}
        for q in questions_result:
            try:
                options = json.loads(q.question_options) if q.question_options else []
            except json.JSONDecodeError:
                options = []
            
            questions[str(q.id)] = {
                "question_text": q.question_text,
                "options": options
            }
        
        # Then get user responses
        responses_query = text("""
            SELECT
                r.id as user_id,
                r.user_name,
                g.game_name,
                GROUP_CONCAT(DISTINCT p.project_name) as project_names,
                GROUP_CONCAT(DISTINCT l.store_name) as location_names,
                GROUP_CONCAT(DISTINCT d.device_model) as device_names
            FROM registrations r
            JOIN responses res
                ON res.user_id = r.id
                AND res.game_id = :game_id
            JOIN games g
                ON g.uuid = res.game_id
            LEFT JOIN projects p
                ON JSON_CONTAINS(r.project_ids, JSON_QUOTE(p.project_id), '$')
            LEFT JOIN locations l
                ON JSON_CONTAINS(r.location_ids, JSON_QUOTE(l.location_id), '$')
            LEFT JOIN devices d
                ON JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(d.device_id), '$')
            WHERE r.client_id = :client_id
            AND JSON_CONTAINS(r.project_ids, JSON_QUOTE(:project_id), '$')
            AND JSON_CONTAINS(r.location_ids, JSON_QUOTE(:location_id), '$')
            AND JSON_CONTAINS(r.kiosk_ids, JSON_QUOTE(:device_id), '$')
            GROUP BY r.id, r.user_name, g.game_name
        """)

        result = db.session.execute(
            responses_query,
            {
                "client_id": client_id,
                "project_id": project_id,
                "location_id": location_id,
                "device_id": device_id,
                "game_id": game_id
            }
        )

        # Get all answers for these users and this game
        user_ids = []
        user_map = {}
        for row in result:
            user_map[str(row.user_id)] = {
                "user_name": row.user_name,
                "game_name": row.game_name,
                "project_names": row.project_names.split(',') if row.project_names else [],
                "location_names": row.location_names.split(',') if row.location_names else [],
                "device_names": row.device_names.split(',') if row.device_names else [],
                "answers": {}
            }
            user_ids.append(str(row.user_id))

        if not user_ids:
            return {
                "client_id": client_id,
                "project_id": project_id,
                "location_id": location_id,
                "device_id": device_id,
                "game_id": game_id,
                "questions": [{"id": k, **v} for k, v in questions.items()],
                "count": 0,
                "data": []
            }, 200

        # Get all answers for these users and this game
        answers_query = text("""
            SELECT user_id, answers 
            FROM responses 
            WHERE user_id IN :user_ids 
            AND game_id = :game_id
        """)

        answers_result = db.session.execute(
            answers_query,
            {
                "user_ids": tuple(user_ids),
                "game_id": game_id
            }
        )

        # Process answers
        for user_id, answer_json in answers_result:
            try:
                answer = json.loads(answer_json) if answer_json else {}
                if str(user_id) in user_map:
                    user_map[str(user_id)]["answers"].update(answer)
            except json.JSONDecodeError:
                continue

        # Format the final response
        data = []
        for user_id, user_data in user_map.items():
            formatted_answers = []
            for q_id, q_data in questions.items():
                answer_value = user_data["answers"].get(q_id)
                
                formatted_answer = {
                    "question_id": q_id,
                    "question_text": q_data["question_text"],
                    "options": q_data["options"],
                    "answer": answer_value,
                    "answer_text": answer_value if answer_value is not None else "Not answered"
                }
                
                # If the question has options and we have an answer, find the matching option text
                if answer_value is not None and q_data["options"]:
                    try:
                        if isinstance(q_data["options"], list):
                            # For simple Yes/No options
                            if answer_value in q_data["options"]:
                                formatted_answer["answer_text"] = answer_value
                            # For options that are dictionaries
                            elif any(isinstance(opt, dict) for opt in q_data["options"]):
                                for opt in q_data["options"]:
                                    if isinstance(opt, dict) and str(opt.get('value')) == str(answer_value):
                                        formatted_answer["answer_text"] = opt.get('text', str(answer_value))
                                        break
                    except Exception as e:
                        print(f"Error processing answer for question {q_id}: {e}")
                        formatted_answer["answer_text"] = str(answer_value)
                
                formatted_answers.append(formatted_answer)
            
            data.append({
                "user_name": user_data["user_name"],
                "game_name": user_data["game_name"],
                "project_names": user_data["project_names"],
                "location_names": user_data["location_names"],
                "device_names": user_data["device_names"],
                "answers": formatted_answers
            })

        return {
            "client_id": client_id,
            "project_id": project_id,
            "location_id": location_id,
            "device_id": device_id,
            "game_id": game_id,
            "questions": [{"id": k, **v} for k, v in questions.items()],
            "count": len(data),
            "data": data
        }, 200