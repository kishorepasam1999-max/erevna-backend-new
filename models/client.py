from extensions import db
from datetime import datetime
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)

    title = db.Column(db.String(50))
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120))
    company_name = db.Column(db.String(200))

    contact_name = db.Column(db.String(200))
    primary_email = db.Column(db.String(200), nullable=False)
    secondary_email = db.Column(db.String(200))

    industry = db.Column(db.String(200))
    client_admin = db.Column(db.String(200))

    primary_contact_number = db.Column(db.String(50))
    secondary_contact_number = db.Column(db.String(50))

    company_team_size = db.Column(db.Integer)
    pincode = db.Column(db.String(20))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))

    additional_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
