from datetime import datetime
from extensions import db
import uuid

class Location(db.Model):
    __tablename__ = "locations"

    location_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.uuid'), nullable=False)  # Fixed this line
    
    # Partner Information
    # partner_id = db.Column(db.String(50), nullable=False, index=True)
    partner_name = db.Column(db.String(200), nullable=False)
    
    # Store Information
    store_name = db.Column(db.String(200), nullable=False)
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    
    # Contact Information
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    store_manager_name = db.Column(db.String(200))
    store_manager_contact = db.Column(db.String(50))
    
    # Geolocation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Operational Details
    opening_date = db.Column(db.Date)
    store_size_sqft = db.Column(db.Float)
    number_of_employees = db.Column(db.Integer)
    hours_of_operation = db.Column(db.String(200))
    
    # Classification
    partner_type = db.Column(db.String(100))
    location_status = db.Column(db.String(50), default="Active")  # e.g., Active, Inactive, Coming Soon
    
    # Additional Information
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Location, self).__init__(**kwargs)
        if not self.location_id:
            self.location_id = str(uuid.uuid4())

    # Add this inside your Location class
    @property
    def is_active(self):
        """Backward compatibility property that maps to location_status"""
        return self.location_status == "Active"

    @is_active.setter
    def is_active(self, value):
        """Set the active status (maps to location_status)"""
        self.location_status = "Active" if value else "Inactive"
      

    def serialize(self):
        return {
            "location_id": self.location_id,
            "client_id":self.client_id,
            "partner_name": self.partner_name,
            "store_name": self.store_name,
            "address": {
                "line1": self.address_line1,
                "line2": self.address_line2,
                "city": self.city,
                "state": self.state,
                "zip_code": self.zip_code,
                "country": self.country,
                "region": self.region,
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "contact": {
                "phone": self.phone_number,
                "email": self.email,
                "store_manager": self.store_manager_name,
                "manager_contact": self.store_manager_contact
            },
            "details": {
                "opening_date": self.opening_date.isoformat() if self.opening_date else None,
                "store_size_sqft": self.store_size_sqft,
                "employee_count": self.number_of_employees,
                "hours": self.hours_of_operation,
                "partner_type": self.partner_type,
                "status": self.location_status
            },
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
    }
        

    def __repr__(self):
        return f"<Location {self.store_name} ({self.city}, {self.country})>"