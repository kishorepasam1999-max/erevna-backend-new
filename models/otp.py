# from extensions import db
# from datetime import datetime, timedelta

# class OTP(db.Model):
#     __tablename__ = "otps"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
#     otp_code = db.Column(db.String(6), nullable=False)
#     expires_at = db.Column(db.DateTime, nullable=False)
#     is_used = db.Column(db.Boolean, default=False)

#     @staticmethod
#     def generate():
#         import random
#         return str(random.randint(100000, 999999))


from extensions import db
from datetime import datetime
import random

class OTP(db.Model):
    __tablename__ = "otps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship("User", backref=db.backref("otps", lazy=True))

    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))

