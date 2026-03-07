# from flask_restx import Namespace, Resource, fields
# from flask import request
# from datetime import date
# from extensions import db
# from models.registration import Registration

# registration_ns = Namespace(
#     "registration",
#     description="User Registration APIs"
# )

# register_model = registration_ns.model("Register", {
#     "user_name": fields.String(required=True),
#     "email": fields.String(required=True),
#     "dob": fields.String(required=True, description="YYYY-MM-DD"),
#     "password": fields.String(required=True),
#     "confirmPassword": fields.String(required=True),

#     "client_id": fields.String(required=True),

#     "project_ids": fields.List(fields.String, required=True),
#     "location_ids": fields.List(fields.String, required=True),
#     "kiosk_ids": fields.List(fields.String, required=True),
#     "game_ids": fields.List(fields.String, required=True),
# })


# def calculate_age(dob):
#     today = date.today()
#     return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# @registration_ns.route("/")
# class Register(Resource):

#     @registration_ns.expect(register_model)
#     def post(self):
#         data = request.json or {}

#         user_name = data.get("user_name")
#         email = data.get("email")
#         dob_str = data.get("dob")
#         password = data.get("password")
#         confirm_password = data.get("confirmPassword")

#         client_id = data.get("client_id")
#         project_ids = data.get("project_ids", [])
#         location_ids = data.get("location_ids", [])
#         kiosk_ids = data.get("kiosk_ids", [])
#         game_ids = data.get("game_ids", [])

#         # ✅ Required field validation
#         if not all([user_name, email, dob_str, password, confirm_password, client_id]):
#             return {"message": "Missing required fields"}, 400

#         if not (project_ids and location_ids and kiosk_ids and game_ids):
#             return {"message": "Project, Location, Kiosk, Game must not be empty"}, 400

#         # Password check
#         if password != confirm_password:
#             return {"message": "Passwords do not match"}, 400

#         # DOB parse
#         try:
#             dob = date.fromisoformat(dob_str)
#         except ValueError:
#             return {"message": "DOB must be YYYY-MM-DD"}, 400

#         # Email uniqueness
#         if Registration.query.filter_by(email=email).first():
#             return {"message": "Email already registered"}, 400

#         # ✅ Create user
#         reg = Registration(
#             user_name=user_name,
#             email=email,
#             dob=dob,
#             age=calculate_age(dob),
#             client_id=client_id
#         )
#         reg.set_password(password)

#         db.session.add(reg)
#         db.session.flush()  # 👈 get user_id before commit

#         # ✅ Insert mappings
#         for pid in project_ids:
#             db.session.add(Project(user_id=reg.id, project_id=pid))

#         for lid in location_ids:
#             db.session.add(ProjectLocation(user_id=reg.id, location_id=lid))

#         for kid in kiosk_ids:
#             db.session.add(ProjectKiosk(user_id=reg.id, kiosk_id=kid))

#         for gid in game_ids:
#             db.session.add(ProjectGame(user_id=reg.id, game_id=gid))

#         db.session.commit()

#         return {
#             "message": "Registration successful",
#             "age": reg.age
#         }, 201

from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import date
from extensions import db
from models.registration import Registration

# -------------------------------
# Namespace
# -------------------------------
registration_ns = Namespace(
    "registration",
    description="User Registration APIs"
)

# -------------------------------
# Request Model (Swagger)
# -------------------------------
register_model = registration_ns.model("Register", {
    "user_name": fields.String(required=True),
    "email": fields.String(required=True),
    "dob": fields.String(required=True, description="YYYY-MM-DD"),
    "password": fields.String(required=True),
    "confirmPassword": fields.String(required=True),
    "client_id": fields.String(required=True),

    "project_ids": fields.List(fields.String, required=True),
    "location_ids": fields.List(fields.String, required=True),
    "kiosk_ids": fields.List(fields.String, required=True),
    "game_ids": fields.List(fields.String, required=True),
})

# -------------------------------
# Helper
# -------------------------------
def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )

# -------------------------------
# Routes
# -------------------------------
@registration_ns.route("/")
class Register(Resource):

    @registration_ns.expect(register_model)
    def post(self):
        data = request.json or {}

        # -------------------------------
        # Extract fields
        # -------------------------------
        user_name = data.get("user_name")
        email = data.get("email")
        dob_str = data.get("dob")
        password = data.get("password")
        confirm_password = data.get("confirmPassword")
        client_id = data.get("client_id")

        project_ids = data.get("project_ids")
        location_ids = data.get("location_ids")
        kiosk_ids = data.get("kiosk_ids")
        game_ids = data.get("game_ids")

        # -------------------------------
        # Validations
        # -------------------------------
        if not all([
            user_name, email, dob_str, password,
            confirm_password, client_id
        ]):
            return {"message": "Missing required fields"}, 400

        if password != confirm_password:
            return {"message": "Passwords do not match"}, 400

        if not all([
            isinstance(project_ids, list) and project_ids,
            isinstance(location_ids, list) and location_ids,
            isinstance(kiosk_ids, list) and kiosk_ids,
            isinstance(game_ids, list) and game_ids
        ]):
            return {
                "message": "project_ids, location_ids, kiosk_ids, game_ids must be non-empty arrays"
            }, 400

        # -------------------------------
        # Parse DOB
        # -------------------------------
        try:
            dob = date.fromisoformat(dob_str)
        except ValueError:
            return {"message": "DOB must be YYYY-MM-DD"}, 400

        # -------------------------------
        # Check Email
        # -------------------------------
        if Registration.query.filter_by(email=email).first():
            return {"message": "Email already registered"}, 400

        # -------------------------------
        # Create Registration
        # -------------------------------
        try:
            registration = Registration(
                user_name=user_name,
                email=email,
                dob=dob,
                age=calculate_age(dob),
                client_id=client_id,

                # ✅ JSON arrays saved directly
                project_ids=project_ids,
                location_ids=location_ids,
                kiosk_ids=kiosk_ids,
                game_ids=game_ids
            )

            registration.set_password(password)

            db.session.add(registration)
            db.session.commit()

            return {
                "success": True,
                "message": "Registration successful",
                "registration_id": registration.id,
                "counts": {
                    "projects": len(project_ids),
                    "locations": len(location_ids),
                    "kiosks": len(kiosk_ids),
                    "games": len(game_ids)
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": "Registration failed",
                "error": str(e)
            }, 500
