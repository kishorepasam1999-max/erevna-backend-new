from datetime import datetime
from extensions import db

class Metric(db.Model):
    """Tracks which metrics are enabled for each project"""
    __tablename__ = "metrics"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
   
    metric_name = db.Column(db.String(100), nullable=False)  # e.g., 'response_time'
    
    
    def serialize(self):
        return {
            "id": self.id,
            
            "metric_name": self.metric_name,
            
        }