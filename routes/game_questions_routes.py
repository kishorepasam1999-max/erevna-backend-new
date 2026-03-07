# # api/game_questions.py
# from utils.validators import validate
# from flask_restx import Namespace, Resource, fields, reqparse
# from flask import request
# from extensions import db
# from models.game_question import GameQuestion
# from datetime import datetime
# # Add this import at the top of the file with other imports
# from werkzeug.datastructures import FileStorage

# api = Namespace("GameQuestions", description="Game Questions Management API")

# # Swagger / API Model for single question
# # question_model = api.model("GameQuestion", {
# #     "id": fields.String(readonly=True),
# #     "client_id": fields.String(required=True),
# #     "project_id": fields.String(required=True),
# #     "game_id": fields.String(required=True),
# #     "question": fields.String(required=True),
# #     "options": fields.List(fields.String),
# #     "status": fields.String,
# #     "created_at": fields.DateTime(readonly=True),
# # })

# question_item_model = api.model('QuestionItem', {
#     'text': fields.String(required=True, description='The question text'),
#     'options': fields.List(fields.String, required=True, description='List of options')
# })

# question_model = api.model("GameQuestion", {
#     "id": fields.String(readonly=True),
#     "client_id": fields.String(required=True),
#     "project_id": fields.String(required=True),
#     "game_id": fields.String(required=True),
#     "question": fields.String(required=True),
#     "options": fields.List(fields.String, default=list, required=True),
#     "status": fields.String,
#     "created_at": fields.DateTime(readonly=True),
# })

# # Swagger / API Model for multiple questions POST
# multi_question_model = api.model("MultiGameQuestion", {
#     "client_id": fields.String(required=True),
#     "project_id": fields.String(required=True),
#     "game_id": fields.String(required=True),
#     # "questions": fields.List(fields.String, required=True, description="List of questions"),
#     "questions": fields.List(fields.Nested(api.model('QuestionItem', {
#         'text': fields.String(required=True, description='The question text'),
#         'options': fields.List(fields.String, required=True, description='List of options')
#     }))),
#     "status": fields.String
# })

# excel_upload_parser = reqparse.RequestParser()
# excel_upload_parser.add_argument('file', 
#                                type=FileStorage, 
#                                location='files', 
#                                required=True,
#                                help='Excel file is required')
# excel_upload_parser.add_argument('client_id', type=str, required=True, help='Client ID is required')
# excel_upload_parser.add_argument('project_id', type=str, required=True, help='Project ID is required')
# excel_upload_parser.add_argument('game_id', type=str, required=True, help='Game ID is required')

# # ------------------ LIST / CREATE ------------------
# @api.route("")
# class GameQuestionList(Resource):

#     @api.marshal_list_with(question_model)
#     def get(self):
#         """Get questions with optional filtering"""
#         query = GameQuestion.query
    
#         # Filter by client_id if provided
#         if client_id := request.args.get('client_id'):
#             query = query.filter_by(client_id=client_id)
            
#         # Filter by project_id if provided
#         if project_id := request.args.get('project_id'):
#             query = query.filter_by(project_id=project_id)
            
#         # Filter by game_id if provided
#         if game_id := request.args.get('game_id'):
#             query = query.filter_by(game_id=game_id)
            
#         # Filter by status if provided
#         if status := request.args.get('status'):
#             query = query.filter_by(status=status)
            
#         return query.all()

#     @api.expect(multi_question_model, validate=False)
#     def post(self):
#         """Create one or more questions"""
#         try:
#             data = request.json
#             client_id = data.get("client_id")
#             project_id = data.get("project_id")
#             game_id = data.get("game_id")
#             questions_list = data.get("questions", [])
#             status = data.get("status", "Active")

#             # Basic validation
#             # if not client_id or not project_id or not game_id:
#             #     return {"message": "client_id, project_id, and game_id are required"}, 400
#             # if not questions_list or not isinstance(questions_list, list):
#             #     return {"message": "questions must be a non-empty list"}, 400

#             if not all([client_id, project_id, game_id]):
#                 return {"message": "client_id, project_id, and game_id are required"}, 400
#             if not questions_list or not isinstance(questions_list, list):
#                 return {"message": "questions must be a non-empty list"}, 400
#             created_questions = []
#             for q_data in questions_list:
#                 if not q_data.get('text', '').strip():
#                     continue

#             created_questions = []
#             for q_text in questions_list:
#                 if not q_text.strip('text', '').strip():
#                     continue
#                 q = GameQuestion(
#                     client_id=client_id,
#                     project_id=project_id,
#                     game_id=game_id,
#                     question=q_data['text'].strip(),
#                     options=q_data.get('options', []),  # Add options
#                     status=status
#                 )
#                 db.session.add(q)
#                 created_questions.append(q)

#             db.session.commit()

#             return {
#                 "message": f"{len(created_questions)} question(s) added successfully",
#                 "question_ids": [q.id for q in created_questions]
#             }, 201

#         except Exception as e:
#             db.session.rollback()
#             import traceback
#             return {
#                 "error": str(e),
#                 "trace": traceback.format_exc()
#             }, 500

# # ------------------ SINGLE QUESTION CRUD ------------------
# @api.route("/<string:question_id>")
# @api.param("question_id", "Question UUID")
# class GameQuestionDetail(Resource):

#     @api.marshal_with(question_model)
#     def get(self, question_id):
#         """Get question by ID"""
#         return GameQuestion.query.filter_by(id=question_id).first_or_404()

#     @api.expect(question_model)
#     def put(self, question_id):
#         """Update question"""
#         try:
#             question = GameQuestion.query.filter_by(id=question_id).first_or_404()
#             data = request.json
#             for key, value in data.items():
#                 if hasattr(question, key):
#                     setattr(question, key, value)
#             db.session.commit()
#             return {"message": "Question updated successfully"}
#         except Exception as e:
#             db.session.rollback()
#             import traceback
#             return {
#                 "error": str(e),
#                 "trace": traceback.format_exc()
#             }, 500

#     def delete(self, question_id):
#         """Delete question"""
#         question = GameQuestion.query.filter_by(id=question_id).first_or_404()
#         db.session.delete(question)
#         db.session.commit()
#         return {"message": "Question deleted successfully"}, 200

# # ------------------ FILTER ------------------
# @api.route("/filter")
# class GameQuestionFilter(Resource):
#     def get(self):
#         client_id = request.args.get("client_id")
#         project_id = request.args.get("project_id")
#         game_id = request.args.get("game_id")

#         query = GameQuestion.query
#         if client_id:
#             query = query.filter_by(client_id=client_id)
#         if project_id:
#             query = query.filter_by(project_id=project_id)
#         if game_id:
#             query = query.filter_by(game_id=game_id)

#         questions = query.all()
#         return {
#             "success": True,
#             "count": len(questions),
#             "questions": [
#                 {
#                     "id": q.id,
#                     "question": q.question,
#                     "options": q.options if q.options else [],  # Include options
#                     "status": q.status
#                 } for q in questions
#             ]
#         }


# # Export endpoint
# @api.route("/export-questions")
# class ExportQuestions(Resource):
#     def get(self):
#         try:
#             # Get query parameters
#             client_id = request.args.get('client_id')
#             project_id = request.args.get('project_id')
#             game_id = request.args.get('game_id')
            
#             # Build query
#             query = GameQuestion.query
            
#             if client_id:
#                 query = query.filter_by(client_id=client_id)
#             if project_id:
#                 query = query.filter_by(project_id=project_id)
#             if game_id:
#                 query = query.filter_by(game_id=game_id)
                
#             questions = query.all()
            
#             # Prepare data for Excel
#             data = []
#             for q in questions:
#                 data.append({
#                     'Question': q.question,
#                     'Options': ' | '.join(q.options.get('options', [])) if q.options else ''
#                 })
                
#             if not data:
#                 return {"success": False, "message": "No questions found"}, 404
                
#             # Create Excel file
#             output = io.BytesIO()
#             df = pd.DataFrame(data)
#             df.to_excel(output, index=False, engine='openpyxl')
#             output.seek(0)
            
#             # Generate filename
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             filename = f"questions_export_{timestamp}.xlsx"

#             # Send file
#             return send_file(
#                 output,
#                 mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#                 as_attachment=True,
#                 download_name=filename
#             )
#         except Exception as e:
#             return {"success": False, "message": str(e)}, 500

# @api.route('/import')
# class ImportQuestions(Resource):
#     @api.expect(excel_upload_parser)
#     def post(self):
#         args = excel_upload_parser.parse_args()
#         excel_file = args['file']
        
#         try:
#             # Your existing import logic here
#             # For example:
#             # df = pd.read_excel(excel_file)
#             # Process the data...
            
#             return {
#                 "success": True,
#                 "message": "Questions imported successfully"
#             }, 200
            
#         except Exception as e:
#             return {
#                 "success": False,
#                 "message": f"Error importing questions: {str(e)}"
#             }, 400

from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.game_question import GameQuestion
import io
import pandas as pd
from flask import request
from werkzeug.datastructures import FileStorage
from flask_restx import reqparse

api = Namespace("game-questions", description="Game Questions API")

# ------------------------------------------------------------------
# OUTPUT MODEL (USED ONLY FOR RESPONSES)
# ------------------------------------------------------------------
game_question_response = api.model("GameQuestionResponse", {
    "id": fields.String,
    "client_id": fields.String,
    "project_id": fields.String,
    "game_id": fields.String,
    "question": fields.String,
    "options": fields.List(fields.String(), attribute="safe_options"),
    "status": fields.String,
    "created_at": fields.DateTime
})

# ------------------------------------------------------------------
# INPUT MODELS (REQUEST ONLY)
# ------------------------------------------------------------------
question_input = api.model("QuestionInput", {
    "text": fields.String(required=True),
    "options": fields.List(fields.String, required=True)
})

bulk_question_input = api.model("BulkQuestionInput", {
    "client_id": fields.String(required=True),
    "project_id": fields.String(required=True),
    "game_id": fields.String(required=True),
    "questions": fields.List(fields.Nested(question_input), required=True),
    "status": fields.String
})

question_update_input = api.model("QuestionUpdateInput", {
    "question": fields.String,
    "options": fields.List(fields.String),
    "status": fields.String
})

# ------------------ EXCEL UPLOAD PARSER ------------------
excel_upload_parser = reqparse.RequestParser()
excel_upload_parser.add_argument(
    'file',
    type=FileStorage,
    location='files',
    required=True,
    help='Excel file is required'
)
excel_upload_parser.add_argument('client_id', required=False)
excel_upload_parser.add_argument('project_id', required=False)
excel_upload_parser.add_argument('game_id', required=False)


# ------------------------------------------------------------------
# LIST + CREATE
# ------------------------------------------------------------------
@api.route("")
class GameQuestionList(Resource):

   
    @api.marshal_list_with(game_question_response)
    def get(self):
        return GameQuestion.query.all()

    @api.expect(bulk_question_input, validate=True)
    def post(self):
        data = request.json

        created = []
        try:
            for item in data["questions"]:
                text = item.get("text", "").strip()
                options = item.get("options", [])

                if not text or not isinstance(options, list):
                    continue

                q = GameQuestion(
                    client_id=data["client_id"],
                    project_id=data["project_id"],
                    game_id=data["game_id"],
                    question=text,
                    options=options,
                    status=data.get("status", "Active")
                )
                db.session.add(q)
                created.append(q)

            db.session.commit()

            return {
                "message": f"{len(created)} questions created",
                "ids": [q.id for q in created]
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# ------------------------------------------------------------------
# SINGLE ITEM
# ------------------------------------------------------------------
@api.route("/<string:question_id>")
class GameQuestionDetail(Resource):

    @api.marshal_with(game_question_response)
    def get(self, question_id):
        q = GameQuestion.query.filter_by(id=question_id).first_or_404()
        if not isinstance(q.options, list):
            q.options = []
        return q

    @api.expect(question_update_input, validate=True)
    def put(self, question_id):
        q = GameQuestion.query.filter_by(id=question_id).first_or_404()
        data = request.json

        if "question" in data:
            q.question = data["question"]
        if "options" in data:
            q.options = data["options"]
        if "status" in data:
            q.status = data["status"]

        db.session.commit()
        return {"message": "Question updated successfully"}

    def delete(self, question_id):
        q = GameQuestion.query.filter_by(id=question_id).first_or_404()
        db.session.delete(q)
        db.session.commit()
        return {"message": "Question deleted successfully"}

@api.route("/import-excel")
class ImportQuestions(Resource):

    @api.expect(excel_upload_parser)
    def post(self):
        args = excel_upload_parser.parse_args()

        excel_file = args['file']
        client_id = args['client_id']
        project_id = args['project_id']
        game_id = args['game_id']

        df = pd.read_excel(excel_file, engine="openpyxl")

        created = []

        for _, row in df.iterrows():
            text = str(row["question"]).strip()
            if not text:
                continue

            options = [
                str(row[c]).strip()
                for c in ["option1", "option2", "option3", "option4"]
                if c in df.columns and pd.notna(row[c])
            ]

            q = GameQuestion(
                client_id=client_id,
                project_id=project_id,
                game_id=game_id,
                question=text,
                options=options,
                status="Active"
            )

            db.session.add(q)
            created.append(q)

        db.session.commit()

        return {
            "success": True,
            "count": len(created)
        }, 201
