from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db, mail, bcrypt
from models.user import User
from flask_jwt_extended import create_access_token, decode_token
from flask_mail import Message
from datetime import timedelta

api = Namespace(
    "PasswordReset",
    description="Password reset: send reset link & confirm new password"
)

# -------------------------
# Swagger Models
# -------------------------
reset_request_model = api.model("ResetPasswordEmailModel", {
    "email": fields.String(required=True, description="Registered user email")
})

reset_password_model = api.model("ResetPasswordModel", {
    "token": fields.String(required=True, description="Reset token received via email"),
    "new_password": fields.String(required=True, description="New password")
})

response_model = api.model("PasswordResetResponse", {
    "success": fields.Boolean,
    "message": fields.String
})


# -------------------------
# STEP 1: SEND RESET LINK
# -------------------------
@api.route('/send-link')
class SendResetLink(Resource):

    @api.expect(reset_request_model, validate=True)
    @api.marshal_with(response_model)
    def post(self):
        data = request.json
        email = data.get("email")

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"success": False, "message": "Email not found"}, 404

        # Create a JWT token valid for 30 minutes
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=30)
        )

        reset_link = f"http://localhost:5173/reset-password?token={token}"

        print("Received token:", token)

        # Send reset email
        msg = Message(
            subject="Password Reset Request",
            recipients=[email],
            body=f"""Hello,

You requested a password reset.

Click the link below to reset your password:
{reset_link}

This link is valid for 30 minutes.

If you did not request this, ignore this email.
"""
        )

        mail.send(msg)

        return {
            "success": True,
            "message": "Password reset link sent to your email."
        }, 200


# -------------------------
# STEP 2: RESET PASSWORD
# -------------------------
@api.route('/confirm')
class ConfirmReset(Resource):

    @api.expect(reset_password_model, validate=True)
    @api.marshal_with(response_model)
    def post(self):
        data = request.json
        token = data.get("token")
        new_password = data.get("new_password")

        print("Frontend sent token:", token)

        try:
            # ❗ Correct: Flask-JWT-Extended does NOT support verify=True
            decoded = decode_token(token)
            print(decoded)

            user_id = int(decoded["sub"])

        except Exception as e:
            print("Decode error:", e)
            return {"success": False, "message": "Invalid or expired token"}, 400

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found"}, 404

        # Update password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()

        return {
            "success": True,
            "message": "Password updated successfully"
        }, 200
