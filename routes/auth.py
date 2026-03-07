from flask_restx import Namespace, Resource, fields
from flask import request
from models.user import User
from models.otp import OTP
from services.email_service import send_otp_email
from datetime import datetime, timedelta
from extensions import db
from flask_jwt_extended import create_access_token
from sqlalchemy import or_


api = Namespace(
    "Auth",
    description="User Authentication APIs (Signup, Signin)"
)

# Swagger Models
signup_model = api.model("SignupModel", {
    "name": fields.String(required=True, description="Full name of the user"),
    "email": fields.String(required=True, description="User email address"),
    "organization": fields.String(description="Organization / Company name"),
    "role": fields.String(description="User role (research_manager, game_team, etc.)"),
    "password": fields.String(required=True, description="Password")
})

# signin_model = api.model("SigninModel", {
#     "email": fields.String(required=True, description="User email"),
#     "password": fields.String(required=True, description="Account password")
# })

signin_model = api.model("SigninModel", {
    "identifier": fields.String(required=True, description="Email or Name"),
    "password": fields.String(required=True, description="Account password")
})

signin_response = api.model("SigninResponse", {
    "success": fields.Boolean,
    "token": fields.String,
    "user": fields.Raw
})

signup_response = api.model("SignupResponse", {
    "success": fields.Boolean,
    "message": fields.String
})

verify_otp_model = api.model("VerifyOTPModel", {
    "identifier": fields.String(required=True, description="User Email or Name"),
    "otp": fields.String(required=True, description="6-digit OTP")
})



# --------------------------------------------------------------------------
# SIGNUP
# --------------------------------------------------------------------------
@api.route('/signup')
class Signup(Resource):

    @api.expect(signup_model, validate=True)
    @api.response(201, "User created successfully", signup_response)
    @api.response(400, "Email already exists")
    def post(self):
        """Register a new user"""
        data = request.json

        if User.query.filter_by(email=data["email"]).first():
            return {"success": False, "message": "Email already exists"}, 400
        
        user = User(
            name=data["name"],
            email=data["email"],
            organization=data.get("organization"),
            role=data.get("role", "user")
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        return {"success": True, "message": "Account created successfully"}, 201

@api.route('/signin')
class Signin(Resource):

    @api.expect(signin_model, validate=True)
    @api.doc(consumes=['application/json'])
    @api.response(200, "OTP Sent")
    @api.response(401, "Invalid credentials")
    def post(self):
        """Step 1: Validate user → Generate OTP → Email OTP"""
        data = request.get_json()

        identifier = data.get("identifier")  # name OR email
        password = data.get("password")

        # Validate user using EMAIL OR NAME
        user = User.query.filter(
            or_(
                User.email == identifier,
                User.name == identifier
            )
        ).first()

        if not user or not user.check_password(password):
            return {"success": False, "message": "Invalid name/email or password"}, 401

        # Delete previous OTPs
        OTP.query.filter_by(user_id=user.id, is_used=False).delete()

        # Generate OTP
        otp = OTP.generate()
        expires = datetime.utcnow() + timedelta(minutes=5)

        otp_entry = OTP(
            user_id=user.id,
            otp_code=otp,
            expires_at=expires
        )
        db.session.add(otp_entry)
        db.session.commit()

        # Email OTP
        send_otp_email(user.email, otp)

        return {
            "success": True,
            "message": "OTP sent to your registered email.",
            "user_id": user.id,
            "user": user.serialize()
        }, 200



# --------------------------------------------------------------------------
# VERIFY OTP → ISSUE JWT TOKEN
# --------------------------------------------------------------------------
@api.route('/verify-otp')
class VerifyOTP(Resource):

    @api.expect(verify_otp_model, validate=True)
    @api.doc(consumes=['application/json'])
    def post(self):
        """Step 2: Verify OTP → Generate Token"""
        data = request.get_json()
        identifier = data.get("identifier")  # This can be email or name
        otp_input = data.get("otp")

        # Find user by email or name
        user = User.query.filter(
            or_(
                User.email == identifier,
                User.name == identifier
            )
        ).first()

        if not user:
            return {"success": False, "message": "User not found"}, 400

        # Fetch latest OTP for this user
        otp_record = OTP.query.filter_by(
            user_id=user.id,
            is_used=False
        ).order_by(OTP.id.desc()).first()

        if not otp_record:
            return {"success": False, "message": "OTP not found or already used"}, 400
        
        # Check if OTP is expired
        if otp_record.expires_at < datetime.utcnow():
            return {"success": False, "message": "OTP expired"}, 400
        
        # Verify OTP code
        if otp_record.otp_code != otp_input:
            return {"success": False, "message": "Invalid OTP"}, 400

        # Mark OTP as used
        otp_record.is_used = True
        db.session.commit()

        # Generate JWT token
        token = create_access_token(identity=user.id)

        return {
            "success": True,
            "message": "OTP verified successfully",
            "token": token,
            "user": user.serialize()
        }, 200

