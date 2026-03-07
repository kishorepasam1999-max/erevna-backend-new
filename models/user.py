from datetime import datetime
from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    organization = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="user")
    password_hash = db.Column(db.String(255), nullable=False)
    # reset_password_required = db.Column(db.Boolean, default=True)  # New field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
        # NEW FIELDS
    forgot_password_count = db.Column(db.Integer, default=0)
    last_forgot_password = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        # self.reset_password_required = False

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "organization": self.organization,
            "role": self.role,
            "created_at": str(self.created_at),
            # NEW FIELDS
            # "reset_password": self.reset_password_required,
            "forgot_password_count": self.forgot_password_count,
            "last_forgot_password": str(self.last_forgot_password) if self.last_forgot_password else None

        }
