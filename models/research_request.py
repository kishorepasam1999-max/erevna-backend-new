from extensions import db
from datetime import datetime
import uuid
import json


def generate_uuid():
    return str(uuid.uuid4())


class ResearchRequestNew(db.Model):
    __tablename__ = "research_requests_new"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(50), unique=True, default=generate_uuid)

    client_uuid = db.Column(db.String(50))
    client_name = db.Column(db.String(200))
    contact_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(200))
    contact_phone = db.Column(db.String(50))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)

    research_objectives = db.Column(db.JSON)
    target_sample_size = db.Column(db.Integer)
    target_demographics = db.Column(db.String(255))
    preferred_locations = db.Column(db.JSON)

    timeline = db.Column(db.String(255))
    budget_range = db.Column(db.String(100))
    special_requirements = db.Column(db.Text)
    proposed_games = db.Column(db.JSON)

    status = db.Column(db.String(50))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ ADD THESE TWO FIELDS
    appointment_date = db.Column(db.String(50))
    appointment_time = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "client_uuid": self.client_uuid,
            "client_name": self.client_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "title": self.title,
            "description": self.description,
            "research_objectives": self.research_objectives,
            "target_sample_size": self.target_sample_size,
            "target_demographics": self.target_demographics,
            "preferred_locations": self.preferred_locations,
            "timeline": self.timeline,
            "budget_range": self.budget_range,
            "special_requirements": self.special_requirements,
            "proposed_games": self.proposed_games,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,

            # NEW FIELDS
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time
        }
