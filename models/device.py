# In models/kiosk.py
from datetime import datetime
from extensions import db
import uuid

class Device(db.Model):
    __tablename__ = "devices"

    # Primary Key
    device_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Device Identification
    device_type = db.Column(db.String(100), nullable=False)  # e.g., tablet, kiosk, mobile
    device_model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True)
    
    # Location Reference
    location_id = db.Column(db.String(36), db.ForeignKey('locations.location_id'), nullable=False)
    
    # Status Information
    status = db.Column(db.String(50), default="Active")  # Active, Inactive, Maintenance, Retired
    installed_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    
    # Technical Specifications
    os_version = db.Column(db.String(50))
    firmware_version = db.Column(db.String(50))
    
    # Additional Information
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = db.relationship('Location', backref='devices')

    project_kiosk = db.relationship('ProjectKiosk', back_populates='device', uselist=False)

    def __init__(self, **kwargs):
        super(Device, self).__init__(**kwargs)
        if not self.device_id:
            self.device_id = str(uuid.uuid4())

    def serialize(self):
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "device_model": self.device_model,
            "serial_number": self.serial_number,
            "location_id": self.location_id,
            "status": self.status,
            "installed_on": self.installed_on.isoformat() if self.installed_on else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "os_version": self.os_version,
            "ip_address": self.ip_address,
            "firmware_version": self.firmware_version,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Device {self.device_model} ({self.device_type}) - {self.status}>"