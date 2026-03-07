# from flask_restx import Namespace, Resource, fields
# from flask import request
# from extensions import db
# import requests, os, json, re

# api = Namespace("ai-analytics", description="AI based analytics")

# question_model = api.model("AIQuestion", {
#     "question": fields.String(required=True, description="Simple analytics question")
# })

# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# @api.route("/generate-graph")
# class AIGraph(Resource):

#     @api.expect(question_model)
#     def post(self):
#         user_question = request.json.get("question")
#         if not user_question:
#             return {"error": "Question is required"}, 400

#         # ---------------- AI PROMPT ----------------
#         prompt = f"""
# You are an expert MySQL analytics query generator.

# Use ONLY these tables & columns:

# TABLE locations
# - location_id
# - store_name

# TABLE project_kiosks
# - device_id
# - project_id
# - location_id

# TABLE games
# - uuid
# - game_name
# - project_id

# TABLE responses
# - id
# - game_id
# - user_id

# IMPORTANT RELATIONSHIPS:
# - responses.game_id → games.uuid
# - games.project_id → project_kiosks.project_id
# - project_kiosks.location_id → locations.location_id

# STRICT RULES:
# 1. Use ONLY SELECT queries.
# 2. NEVER assume responses has location_id or device_id.
# 3. COUNT customers using COUNT(responses.id).

# METRICS:
# - Customers per location → responses → games → project_kiosks → locations (GROUP BY locations.store_name)
# - Customers per device → responses → games → project_kiosks (GROUP BY project_kiosks.device_id)
# - Customers per game → GROUP BY games.game_name
# - Number of locations → COUNT(locations.location_id)
# - Number of devices → COUNT(project_kiosks.device_id)
# - Number of games → COUNT(games.uuid)

# Choose chartType:
# - totals → bar
# - comparisons → bar
# - distribution → pie

# Return ONLY JSON:
# {{
#   "sql": "SELECT ...",
#   "chartType": "bar | pie",
#   "xAxis": "label",
#   "yAxis": "value"
# }}

# User question: {user_question}
# """


#         # ---------------- AI CALL ----------------
#         try:
#             response = requests.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "meta-llama/llama-3-8b-instruct",
#                     "messages": [{"role": "user", "content": prompt}]
#                 },
#                 timeout=30
#             )
#             raw = response.json()["choices"][0]["message"]["content"]
#         except Exception as e:
#             return {"error": "AI call failed", "details": str(e)}, 500

#         # ---------------- JSON SAFE PARSE ----------------
#         match = re.search(r"\{[\s\S]*?\}", raw)  # non-greedy
#         if not match:
#             return {"error": "AI did not return valid JSON", "raw": raw}, 400

#         try:
#             ai_json = json.loads(match.group(0))
#         except json.JSONDecodeError as e:
#             return {"error": "Failed to parse AI JSON", "details": str(e), "raw": raw}, 400

#         # ---------------- SQL VALIDATION ----------------
#         sql = ai_json.get("sql", "").strip()
#         if not sql.lower().startswith("select"):
#             return {"error": "Only SELECT statements are allowed"}, 400

#         # ---------------- SQL EXECUTION ----------------
#         try:
#             result = db.session.execute(db.text(sql))
#             rows = [dict(row) for row in result.mappings()]
#         except Exception as e:
#             return {"error": "SQL execution failed", "details": str(e), "sql": sql}, 500

#         # ---------------- FORMAT DATA FOR CHART ----------------
#         x_axis = ai_json.get("xAxis", "x").split('.')[-1]
#         y_axis = ai_json.get("yAxis", "y").split('.')[-1]
#         formatted_data = [
#             {x_axis: row.get(x_axis, ""), y_axis: row.get(y_axis, 0)}
#             for row in rows
#         ]

#         return {
#             "chartType": ai_json.get("chartType", "bar"),
#             "xAxis": x_axis,
#             "yAxis": y_axis,
#             "data": formatted_data
#         }


from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
import requests, os, json, re

api = Namespace("ai-analytics", description="AI based analytics")

question_model = api.model("AIQuestion", {
    "question": fields.String(required=True, description="Simple analytics question")
})

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


@api.route("/generate-graph")
class AIGraph(Resource):

    @api.expect(question_model)
    def post(self):
        user_question = request.json.get("question")
        if not user_question:
            return {"error": "Question is required"}, 400

        # ---------------- AI PROMPT ----------------
        prompt = f"""
You are an expert MySQL analytics query generator.

Use ONLY these tables & columns:

TABLE locations
- location_id
- store_name

TABLE project_kiosks
- device_id
- project_id
- location_id

TABLE games
- uuid
- game_name
- project_id

TABLE responses
- id
- game_id
- user_id
- created_at

IMPORTANT RELATIONSHIPS:
- responses.game_id → games.uuid
- games.project_id → project_kiosks.project_id
- project_kiosks.location_id → locations.location_id

STRICT RULES:
1. Use ONLY SELECT queries.
2. EVERY SELECT MUST include a FROM clause.
3. NEVER assume responses has location_id or device_id.
4. COUNT customers using COUNT(responses.id).

FIXED METRICS:
- Number of locations → SELECT COUNT(location_id) AS value FROM locations
- Number of devices → SELECT COUNT(device_id) AS value FROM project_kiosks
- Number of games → SELECT COUNT(uuid) AS value FROM games

DISTRIBUTION METRICS:
- Customers per location → GROUP BY locations.store_name
- Customers per device → GROUP BY project_kiosks.device_id
- Customers per game → GROUP BY games.game_name

CHART TYPES:
- totals → bar
- comparisons → bar
- trends → line
- distribution → pie

Return ONLY JSON:
{{
  "sql": "SELECT ... FROM ...",
  "chartType": "bar | pie | line",
  "xAxis": "label",
  "yAxis": "value"
}}

User question: "{user_question}"
"""

        # ---------------- AI CALL ----------------
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3-8b-instruct",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            raw = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return {"error": "AI call failed", "details": str(e)}, 500

        # ---------------- JSON SAFE PARSE ----------------
        match = re.search(r"\{[\s\S]*?\}", raw)
        if not match:
            return {"error": "AI did not return valid JSON", "raw": raw}, 400

        try:
            ai_json = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            return {"error": "Failed to parse AI JSON", "details": str(e)}, 400

        # ---------------- SQL VALIDATION ----------------
        sql = ai_json.get("sql", "").strip()

        if not sql.lower().startswith("select"):
            return {"error": "Only SELECT queries allowed", "sql": sql}, 400

        if " from " not in sql.lower():
            return {
                "error": "Invalid SQL generated: FROM clause is missing",
                "sql": sql
            }, 400

        # ---------------- HARD SQL SAFETY ----------------
        invalid_patterns = [
            "responses.location_id",
            "responses.device_id",
            "insert ",
            "update ",
            "delete ",
            "drop ",
            "alter "
        ]

        for p in invalid_patterns:
            if p in sql.lower():
                return {
                    "error": "Invalid or unsafe SQL generated",
                    "sql": sql
                }, 400

        # ---------------- SQL EXECUTION ----------------
        try:
            result = db.session.execute(db.text(sql))
            rows = list(result.mappings())
        except Exception as e:
            return {
                "error": "SQL execution failed",
                "details": str(e),
                "sql": sql
            }, 500

        # ---------------- HANDLE COUNT METRICS ----------------
        # Example: Number of locations / devices / games
        if len(rows) == 1 and len(rows[0]) == 1:
            key = list(rows[0].keys())[0]
            return {
                "chartType": ai_json.get("chartType", "bar"),
                "xAxis": "label",
                "yAxis": key,
                "data": [
                    {
                        "label": user_question,
                        key: rows[0][key]
                    }
                ]
            }

        # ---------------- FORMAT GROUP / LINE DATA ----------------
        x_axis = ai_json.get("xAxis", "label").split('.')[-1]
        y_axis = ai_json.get("yAxis", "value").split('.')[-1]

        formatted_data = [
            {
                x_axis: row.get(x_axis),
                y_axis: row.get(y_axis, 0)
            }
            for row in rows
        ]

        return {
            "chartType": ai_json.get("chartType", "bar"),
            "xAxis": x_axis,
            "yAxis": y_axis,
            "data": formatted_data
        }

