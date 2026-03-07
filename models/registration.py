from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# Association Tables
# registration_project = db.Table(
#     'registration_project',
#     db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), primary_key=True),
#     db.Column('project_id', db.String(36), primary_key=True)
# )

# registration_location = db.Table(
#     'registration_location',
#     db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), primary_key=True),
#     db.Column('location_id', db.String(36), primary_key=True)
# )

# registration_kiosk = db.Table(
#     'registration_kiosk',
#     db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), primary_key=True),
#     db.Column('kiosk_id', db.String(36), primary_key=True)
# )

# registration_game = db.Table(
#     'registration_game',
#     db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), primary_key=True),
#     db.Column('game_id', db.String(36), primary_key=True)
# )

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)

    user_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer)

    password_hash = db.Column(db.String(255), nullable=False)

    client_id = db.Column(db.String(36), nullable=False)

    # ✅ JSON ARRAY COLUMNS
    project_ids = db.Column(db.JSON, nullable=False)
    location_ids = db.Column(db.JSON, nullable=False)
    kiosk_ids = db.Column(db.JSON, nullable=False)
    game_ids = db.Column(db.JSON, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
