from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.registration import Registration

# Define the namespace
login_ns = Namespace(
    "login",
    description="User authentication and login operations"
)

# Define the login model
login_model = login_ns.model("Login", {
    "email": fields.String(required=True, description="User's email address"),
    "password": fields.String(required=True, description="User's password")
})

@login_ns.route("/")
class Login(Resource):
    @login_ns.expect(login_model)
    @login_ns.response(200, "Login successful")
    @login_ns.response(400, "Missing email or password")
    @login_ns.response(401, "Invalid credentials")
    def post(self):
        """User login with email and password"""
        data = request.json or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "success": False,
                "message": "Email and password are required"
            }, 400

        user = Registration.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {
                "success": False,
                "message": "Invalid email or password"
            }, 401

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "user_id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "client_id": user.client_id,
                "project_ids": getattr(user, 'project_ids', []),
                "location_ids": getattr(user, 'location_ids', []),
                "kiosk_ids": getattr(user, 'kiosk_ids', []),
                "game_ids": getattr(user, 'game_ids', [])
            }
        }, 200