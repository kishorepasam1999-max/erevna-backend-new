from datetime import datetime
from extensions import db
import uuid
from typing import List, Dict, Optional
from models.employee import Employee
from models.device import Device as Kiosk
from sqlalchemy import JSON
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship



    # ===== 1. Basic Information =====
    # In models/project.py
class Project(db.Model):
    __tablename__ = "projects"

    project_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = db.Column(db.String(200), nullable=False)
    client_id = db.Column(db.String(36), nullable=False)
    client_name = db.Column(db.String(200))
    request_type = db.Column(db.String(50))  # urgent, standard, low_priority
    status = db.Column(db.String(50), default='draft')
    start_date = db.Column(db.DateTime, nullable=True)  # Made nullable
    end_date = db.Column(db.DateTime, nullable=True)    # Made nullable
    required_no_of_hours = db.Column(db.Integer, default=0) 
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    def serialize(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'client_id':self.client_id,
            'client_name': self.client_name,
            'request_type': self.request_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'required_no_of_hours': self.required_no_of_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # ===== 2. Client Mapping =====
    client_id = db.Column(db.String(36), db.ForeignKey('clients.uuid'))
    client_name = db.Column(db.String(200))
    client_contact_person = db.Column(db.String(200))
    client_email = db.Column(db.String(200))
    client_phone = db.Column(db.String(50))
    client_requirements = db.Column(db.Text)

    # In the Project class
    employee = db.relationship('Employee', backref='projects')

    project_users = db.relationship('ProjectUser', back_populates='project', cascade='all, delete-orphan')
    
    # ===== 3. Task Creation =====
    tasks = db.relationship('ProjectTask', backref='project', lazy=True, cascade="all, delete-orphan")
    
    # ===== 4. Locations =====
    locations = db.relationship(
        'ProjectLocation',
        back_populates='project',
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    # ===== 5. Kiosks =====
    kiosks = db.relationship('ProjectKiosk', backref='project', lazy=True, cascade="all, delete-orphan")
    
    # ===== 6. Games =====
    games = db.relationship('ProjectGame', backref='project', lazy=True, cascade="all, delete-orphan")
    
    # ===== 7. Schedule =====
    schedule = db.relationship('ProjectSchedule', backref='project', uselist=False, cascade="all, delete-orphan")
    
    # ===== 8. Quotas =====
    quotas = db.relationship('ProjectQuota', backref='project', lazy=True, cascade="all, delete-orphan")
    
    # ===== 9. Metrics =====
    metrics = db.relationship(
    'ProjectMetric',
    backref='project',
    lazy=True,
    cascade="all, delete-orphan"
)
    
    # ===== 10. Review =====
    review_notes = db.Column(db.Text)
    review_rating = db.Column(db.Integer)  # 1-5 scale
    review_feedback = db.Column(db.Text)
    
    # ===== System Fields =====
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        # if not self.project_id:
        #     self.project_id = str(uuid.uuid4())
        if self.client_id:
            self.sync_client_locations()

    def sync_client_locations(self):
        from models.location import Location  # Import here to avoid circular imports
    
        # Get all active locations for this client
        client_locations = Location.query.filter_by(
            client_id=self.client_id,
            is_active=True
        ).all()
    
        # Add locations that don't already exist for this project
        existing_location_ids = {loc.location_id for loc in self.locations}
    
        for loc in client_locations:
            if str(loc.id) not in existing_location_ids:
                project_location = ProjectLocation(
                project_id=self.id,
                client_id=self.client_id,
                location_id=loc.id,
                timezone=loc.timezone or "UTC",
                status="Active",
                is_primary=False  # You might want to handle this differently
            )
            db.session.add(project_location)
            db.session.commit()
    
    def update_client(self, client_id):
        """Update client and sync locations"""
        self.client_id = client_id
        self.sync_client_locations()
        db.session.commit()
    
    # In Project model's sync_client_locations method
def sync_client_locations(self):
    from models.location import Location
    
    client_locations = Location.query.filter_by(
        client_id=self.client_id,
        is_active=True
    ).all()
    
    existing_location_ids = {loc.location_id for loc in self.locations}
    
    for loc in client_locations:
        if str(loc.id) not in existing_location_ids:
            project_location = ProjectLocation(
                project_id=self.id,
                client_id=self.client_id,
                location_id=loc.id,
                timezone=loc.timezone or "UTC",
                status="Active"
            )
            db.session.add(project_location)
            db.session.flush()  # Get the ID for the new location
            
            # Sync kiosks for this location
            kiosks = Kiosk.query.filter_by(
                location_id=loc.id,
                is_active=True
            ).all()
            
            for kiosk in kiosks:
                project_kiosk = ProjectKiosk(
                    project_id=self.id,
                    location_id=project_location.id,  # Link to project location
                    kiosk_id=kiosk.id,
                    status="Active"
                )
                db.session.add(project_kiosk)

    def serialize(self) -> Dict:
        """Convert the project to a dictionary for JSON serialization"""
        return {
            # 1. Basic Info
            "project_id": self.project_id,
            "project_name": self.project_name,
            "description": self.description,
            "timeline": {
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None
            },
            "project_type": self.project_type,
            "status": self.status,
            
            # 2. Client Mapping
            "client": {
                "client_id": self.client_id,
                "name": self.client_name,
                "contact_person": self.client_contact_person,
                "email": self.client_email,
                "phone": self.client_phone,
                "requirements": self.client_requirements
            },
            
            # 3. Tasks
            "tasks": [task.serialize() for task in self.tasks] if self.tasks else [],
            
            # 4. Locations
            "locations": [loc.serialize() for loc in self.locations] if self.locations else [],
            
            # 5. Kiosks
            "kiosks": [kiosk.serialize() for kiosk in self.kiosks] if self.kiosks else [],
            
            # 6. Games
            "games": [game.serialize() for game in self.games] if self.games else [],
            
            # 7. Schedule
            "schedule": self.schedule.serialize() if self.schedule else None,
            
            # 8. Quotas
            "quotas": [quota.serialize() for quota in self.quotas] if self.quotas else [],
            
            # 9. Metrics
            # "metrics": [metric.serialize() for metric in self.metrics] if self.metrics else [],
            
            # 10. Review
            "review": {
                "notes": self.review_notes,
                "rating": self.review_rating,
                "feedback": self.review_feedback
            } if self.review_notes or self.review_rating or self.review_feedback else None,
            
            # System
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Project {self.project_name} ({self.project_id}) - {self.status}>"


class ProjectUser(db.Model):
    __tablename__ = "project_users"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    department = db.Column(db.String(200))
    designation = db.Column(db.String(200))
    stage = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    employee = db.relationship(
        "Employee",
        back_populates="project_users"
    )
    # employee = db.relationship('Employee', backref=db.backref('project_users', cascade='all, delete-orphan'))
    project = db.relationship('Project', back_populates='project_users')
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "employee_id": self.employee_id,
            "employee_name": self.employee.full_name if self.employee else None,
            "email": self.employee.email if self.employee else None,
            "department": self.department,
            "designation": self.designation,
            "stage": self.stage,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectTask(db.Model):
    """Tasks associated with a project"""
    __tablename__ = "project_tasks"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    stage = db.Column(db.String(100), nullable=False)
    process = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    step = db.Column(db.String(100))
    type = db.Column(db.String(50))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_mandatory = db.Column(db.Boolean, default=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('employees.id'))
    priority = db.Column(db.String(20))  # low, medium, high
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def serialize(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'stage': self.stage,
            'process': self.process,
            'title': self.title,
            'step': self.step,
            'type': self.type,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_mandatory': self.is_mandatory,
            'assigned_to': self.assigned_to,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectLocation(db.Model):
    __tablename__ = "project_locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(
        db.String(36),
            db.ForeignKey("projects.project_id", ondelete="CASCADE"),
            nullable=False
        )
    location_id = db.Column(db.String(36), nullable=True)
    store_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)

    # Relationship (optional)
    project = db.relationship(
        'Project',
        back_populates='locations'
    )
    kiosks = db.relationship('ProjectKiosk', back_populates='location')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'location_id': self.location_id,
            'store_name': self.store_name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'status': self.status,
            
            'is_primary': self.is_primary,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProjectKiosk(db.Model):
    __tablename__ = "project_kiosks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(36), db.ForeignKey('devices.device_id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('project_locations.id'), nullable=False)
    status = db.Column(db.String(50), default='offline')
    last_active = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # project = db.relationship('Project', back_populates='kiosks')
    device = db.relationship('Device', back_populates='project_kiosk')
    location = db.relationship('ProjectLocation', back_populates='kiosks')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'project_id': self.project_id,
            'location_id': self.location_id,
            'device_name': f"{self.device.device_type} {self.device.device_model}" if self.device else None,
            'device_type': self.device.device_type if self.device else None,
            'firmware_version': self.device.firmware_version if self.device else None,
            'status': self.status,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'notes': self.notes
        }


class ProjectGame(db.Model):
    __tablename__ = "project_games"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.project_id"), nullable=False)
    game_id = db.Column(db.String(36), db.ForeignKey("games.uuid"), nullable=False)

    kiosk_ids = db.Column(JSON, nullable=True)
    configuration = db.Column(JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationship to Game
    game = relationship("Game", backref="project_games")

    def serialize(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "game_id": self.game_id,
            "game_name": self.game.game_name if self.game else None,
            "kiosk_ids": self.kiosk_ids,
            "configuration": self.configuration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectSchedule(db.Model):
    """Project schedule, timeline, and session settings"""
    __tablename__ = "project_schedules"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False, unique=True)
    
    # Timeline settings
    start_date = db.Column(db.DateTime, nullable=True)  # Made nullable
    end_date = db.Column(db.DateTime, nullable=True)    # Made nullable
    time_limit_seconds = db.Column(db.Integer, default=300)  # 5 minutes default
    
   
    
    def serialize(self) -> Dict:
        return {
            "project_id": self.project_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "time_limit_seconds": self.time_limit_seconds,
            
        }

class ProjectQuota(db.Model):
    """Project sample quotas and screening criteria"""
    __tablename__ = "project_quotas"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    
    # Only these two fields as requested
    total_samples_needed = db.Column(db.Integer, nullable=False, default=0)
    screening_criteria = db.Column(JSON, default=dict)  # Store criteria as JSON
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def serialize(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "total_samples_needed": self.total_samples_needed,
            "screening_criteria": self.screening_criteria or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ProjectMetric(db.Model):
    """Tracks which metrics are enabled for each project"""
    __tablename__ = "project_metrics"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Changed from metric_name to name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship (if needed)
    # project = db.relationship('Project', back_populates='metrics')
    
    def serialize(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,  # Changed from metric_name to name
            "created_at": self.created_at.isoformat() if self.created_at else None
        }