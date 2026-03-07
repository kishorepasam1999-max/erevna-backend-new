from extensions import db
from datetime import datetime
import json

class ProjectVersion(db.Model):
    __tablename__ = "project_versions"

    id = db.Column(db.Integer, primary_key=True)
    project_uuid = db.Column(db.String(36), db.ForeignKey('projects.project_id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    data = db.Column(db.JSON, nullable=False)  # Stores the complete project state
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    change_note = db.Column(db.Text, nullable=True)

    # Index for faster lookups
    __table_args__ = (
        db.Index('idx_project_version', 'project_uuid', 'version'),
    )

    def __init__(self, **kwargs):
        super(ProjectVersion, self).__init__(**kwargs)
        if isinstance(self.data, dict):
            self.data = json.dumps(self.data)

    def to_dict(self):
        """Convert version data to dictionary"""
        return {
            "id": self.id,
            "project_uuid": self.project_uuid,
            "version": self.version,
            "data": json.loads(self.data) if isinstance(self.data, str) else self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "change_note": self.change_note
        }

    def __repr__(self):
        return f"<ProjectVersion {self.project_uuid} v{self.version}>"